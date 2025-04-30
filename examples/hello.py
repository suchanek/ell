import ell

ell.init(store="./logdir", autocommit=True)


@ell.simple(model="gpt-4o")
def hello(name: str):
    """You are a helpful assistant."""
    return f"Say hello to {name}!"


greeting = hello("Sam Altman")
print(greeting)
