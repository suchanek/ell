"""
Services module containing business logic for the application.
"""

from test_repo.module1.models import User, Admin, Product


def create_user(name, email, age=None):
    """Create a new user."""
    return User(name, email, age)


def create_admin(name, email, department, age=None):
    """Create a new admin."""
    return Admin(name, email, department, age)


def create_product(name, price, description=None):
    """Create a new product."""
    return Product(name, price, description)


def get_user_summary(user):
    """Get a summary of the user."""
    if isinstance(user, Admin):
        return f"Admin: {user.get_display_name()}, Department: {user.department}"
    else:
        return f"User: {user.get_display_name()}"


def calculate_total_price(products):
    """Calculate the total price of a list of products."""
    return sum(product.price for product in products)


def format_product_list(products):
    """Format a list of products for display."""
    return "\n".join([
        f"{product.name}: {product.get_display_price()}"
        for product in products
    ])
