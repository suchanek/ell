"""
Main module for the application.
"""

from test_repo.module1.models import User, Admin, Product
from test_repo.module1.services import create_user, create_admin, create_product, get_user_summary
from test_repo.module2.order import Order, create_order, process_order


def main():
    """Main function to demonstrate the application."""
    # Create users
    user = create_user("John Doe", "john@example.com", 25)
    admin = create_admin("Jane Smith", "jane@example.com", "IT", 30)
    
    # Create products
    products = [
        create_product("Laptop", 1299.99, "High-performance laptop"),
        create_product("Mouse", 24.99, "Wireless mouse"),
        create_product("Keyboard", 49.99, "Mechanical keyboard")
    ]
    
    # Create and process orders
    user_order = create_order(user, products[:2])  # Laptop and Mouse
    admin_order = create_order(admin, products[1:])  # Mouse and Keyboard
    
    # Process orders
    process_order(user_order)
    process_order(admin_order)
    
    # Print summaries
    print("\nUser Information:")
    print(get_user_summary(user))
    print(get_user_summary(admin))
    
    print("\nOrder Summaries:")
    print("User Order:", user_order.get_summary())
    print("Admin Order:", admin_order.get_summary())


if __name__ == "__main__":
    main()
