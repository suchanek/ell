"""
Repository Knowledge Graph Generator

This program scans Python repositories and builds a knowledge graph representing
class relationships and function call inter-relationships. It uses the ell library
with language models to analyze code and extract meaningful relationships.
"""

import argparse
import glob
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from graphviz import Digraph
from pydantic import BaseModel, Field
from tqdm import tqdm

# Define colorblind-friendly color palette
COLORS = {
    "CLASS": "#0072B2",  # Blue
    "FUNCTION": "#E69F00",  # Orange
    "METHOD": "#009E73",  # Green
    "INHERITANCE": "#CC79A7",  # Purple
    "FUNCTION_CALL": "#D55E00",  # Brown
    "USAGE": "#56B4E9",  # Gray
}


class Node(BaseModel):
    """Represents a node in the knowledge graph."""

    id: int
    label: str
    color: str
    type: str = Field(description="Type of node (CLASS, FUNCTION, METHOD)")


class Edge(BaseModel):
    """Represents an edge in the knowledge graph."""

    source: int
    target: int
    label: str
    color: str = Field(description="The color of the edge based on relationship type.")


class KnowledgeGraph(BaseModel):
    """Represents the entire knowledge graph with nodes and edges."""

    nodes: Optional[List[Node]] = Field(default_factory=list)
    edges: Optional[List[Edge]] = Field(default_factory=list)

    def update(self, other: "KnowledgeGraph") -> "KnowledgeGraph":
        """Updates the current graph with the other graph, deduplicating nodes and edges."""
        # Create dictionaries to store unique nodes and edges
        unique_nodes = {node.id: node for node in self.nodes}
        unique_edges = {
            (edge.source, edge.target, edge.label): edge for edge in self.edges
        }

        # Update with nodes and edges from the other graph
        for node in other.nodes:
            unique_nodes[node.id] = node
        for edge in other.edges:
            unique_edges[(edge.source, edge.target, edge.label)] = edge

        return KnowledgeGraph(
            nodes=list(unique_nodes.values()),
            edges=list(unique_edges.values()),
        )

    def draw(self, output_path: str, format: str = "png"):
        """Draw the knowledge graph and save it to the specified path."""
        dot = Digraph(comment="Repository Knowledge Graph")

        # Add nodes
        for node in self.nodes:
            dot.node(str(node.id), node.label, color=node.color)

        # Add edges
        for edge in self.edges:
            dot.edge(
                str(edge.source), str(edge.target), label=edge.label, color=edge.color
            )

        # Add legend
        with dot.subgraph(name="cluster_legend") as legend:
            legend.attr(label="Legend", style="filled", color="lightgrey")
            legend.node("class_node", "Class", color=COLORS["CLASS"], shape="box")
            legend.node(
                "function_node", "Function", color=COLORS["FUNCTION"], shape="box"
            )
            legend.node("method_node", "Method", color=COLORS["METHOD"], shape="box")
            legend.node(
                "inheritance_edge",
                "Inheritance",
                color=COLORS["INHERITANCE"],
                shape="box",
            )
            legend.node(
                "function_call_edge",
                "Function Call",
                color=COLORS["FUNCTION_CALL"],
                shape="box",
            )
            legend.node("usage_edge", "Usage", color=COLORS["USAGE"], shape="box")

        # Render the graph
        dot.render(output_path, format=format, cleanup=True)
        print(f"Graph saved to {output_path}.{format}")


def scan_repository(
    repo_path: str, exclude_dirs: Optional[List[str]] = None
) -> List[str]:
    """
    Scan a repository for Python files.

    Args:
        repo_path: Path to the repository
        exclude_dirs: List of directory names to exclude

    Returns:
        List of Python file paths
    """
    if exclude_dirs is None:
        exclude_dirs = [
            "venv",
            "__pycache__",
            ".git",
            ".github",
            ".vscode",
            "build",
            "dist",
        ]

    python_files = []
    repo_path = os.path.abspath(repo_path)

    print(f"Scanning repository: {repo_path}")

    for root, dirs, files in os.walk(repo_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # Find Python files
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    print(f"Found {len(python_files)} Python files")
    return python_files


def batch_files(files: List[str], batch_size: int = 10) -> List[List[str]]:
    """
    Group files into batches for efficient processing.

    Args:
        files: List of file paths
        batch_size: Number of files per batch

    Returns:
        List of batches, where each batch is a list of file paths
    """
    return [files[i : i + batch_size] for i in range(0, len(files), batch_size)]


def read_file_content(file_path: str) -> str:
    """
    Read the content of a file.

    Args:
        file_path: Path to the file

    Returns:
        Content of the file as a string
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""


import ell


@ell.simple(model="o1-mini")
def extract_relationships(file_contents: List[Tuple[str, str]]):
    """
    Extract class and function relationships from a batch of files using a language model.

    Args:
        file_contents: List of tuples (file_path, file_content)

    Returns:
        JSON string representing the knowledge graph
    """
    return [
        ell.user(
            f"""You are an expert Python code analyzer. Your task is to build a knowledge graph representing class relationships and function call inter-relationships from Python code.

Focus specifically on:
1. Class relationships (inheritance, composition, usage)
2. Function call relationships (which functions call which others)

For each file, identify:
- Classes (color: {COLORS["CLASS"]})
- Functions (color: {COLORS["FUNCTION"]})
- Methods (color: {COLORS["METHOD"]})
- Inheritance relationships (color: {COLORS["INHERITANCE"]})
- Function call relationships (color: {COLORS["FUNCTION_CALL"]})
- Usage relationships (color: {COLORS["USAGE"]})

Analyze the following Python files and extract the relationships:

{chr(10).join([f"File: {path}{chr(10)}```python{chr(10)}{content}{chr(10)}```{chr(10)}" for path, content in file_contents])}

Return a knowledge graph in JSON format that represents these relationships. Each node should have a unique ID, a label, a color based on its type, and a type field. Each edge should have a source node ID, a target node ID, a label describing the relationship, and a color based on the relationship type.

Answer only in this JSON format:
{KnowledgeGraph.model_json_schema()}

Do not wrap your JSON update in back ticks (```)
Do not include any other text.
"""
        )
    ]


def process_files(files: List[str], batch_size: int = 10) -> KnowledgeGraph:
    """
    Process files in batches to build the knowledge graph.

    Args:
        files: List of file paths
        batch_size: Number of files per batch

    Returns:
        KnowledgeGraph object
    """
    batches = batch_files(files, batch_size)
    graph = KnowledgeGraph()

    print(f"Processing {len(files)} files in {len(batches)} batches")

    for i, batch in enumerate(tqdm(batches, desc="Processing batches")):
        # Read file contents
        file_contents = []
        for file_path in batch:
            content = read_file_content(file_path)
            if content:
                file_contents.append((file_path, content))

        if not file_contents:
            continue

        # Extract relationships
        try:
            print(f"Analyzing batch {i+1}/{len(batches)} ({len(file_contents)} files)")
            result = extract_relationships(file_contents)
            
            # Convert result to string if it's not already
            if not isinstance(result, str):
                result = str(result)
            
            # Clean up the result
            result = result.replace("```json", "")
            result = result.replace("```", "")
            
            # Parse the result
            try:
                new_graph = KnowledgeGraph.model_validate_json(result)
                
                # Update the graph
                graph = graph.update(new_graph)
                
                print(
                    f"Batch {i+1} complete. Graph now has {len(graph.nodes)} nodes and {len(graph.edges)} edges"
                )
            except Exception as e:
                print(f"Error parsing result: {e}")
                print(f"Result: {result[:500]}..." if len(result) > 500 else f"Result: {result}")
                
        except Exception as e:
            print(f"Error processing batch {i+1}: {e}")

    return graph


def generate_knowledge_graph(
    repo_path: str,
    output_path: str,
    exclude_dirs: Optional[List[str]] = None,
    batch_size: int = 10,
    format: str = "png",
) -> KnowledgeGraph:
    """
    Generate a knowledge graph from a repository.

    Args:
        repo_path: Path to the repository
        output_path: Path to save the output graph
        exclude_dirs: List of directory names to exclude
        batch_size: Number of files per batch
        format: Output format (png, svg, pdf)

    Returns:
        KnowledgeGraph object
    """
    # Scan repository
    files = scan_repository(repo_path, exclude_dirs)

    # Process files
    graph = process_files(files, batch_size)

    # Draw the graph
    graph.draw(output_path, format)

    return graph


def main():
    """Main function to parse arguments and generate the knowledge graph."""
    parser = argparse.ArgumentParser(
        description="Generate a knowledge graph from a Python repository"
    )
    parser.add_argument("--repo", required=True, help="Path to the repository")
    parser.add_argument(
        "--output",
        default="repo_graph",
        help="Path to save the output graph (without extension)",
    )
    parser.add_argument(
        "--exclude",
        default="venv,__pycache__,.git,.github,.vscode,build,dist",
        help="Comma-separated list of directories to exclude",
    )
    parser.add_argument(
        "--batch-size", type=int, default=5, help="Number of files per batch"
    )
    parser.add_argument(
        "--format", default="png", choices=["png", "svg", "pdf"], help="Output format"
    )

    args = parser.parse_args()

    # Initialize ell
    ell.init(verbose=True, store="./logdir", autocommit=True)

    # Generate knowledge graph
    exclude_dirs = args.exclude.split(",") if args.exclude else None
    generate_knowledge_graph(
        args.repo, args.output, exclude_dirs, args.batch_size, args.format
    )


if __name__ == "__main__":
    main()
