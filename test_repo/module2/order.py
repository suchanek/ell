"""
Order module for handling orders in the application.
"""

from test_repo.module1.models import User, Product
from test_repo.module1.services import calculate_total_price, format_product_list


class Order:
    """Order class representing an order in the system."""
    
    def __init__(self, user, products=None):
        """Initialize a new Order instance."""
        self.user = user
        self.products = products or []
        self.is_completed = False
    
    def add_product(self, product):
        """Add a product to the order."""
        self.products.append(product)
    
    def remove_product(self, product):
        """Remove a product from the order."""
        if product in self.products:
            self.products.remove(product)
    
    def get_total(self):
        """Get the total price of the order."""
        return calculate_total_price(self.products)
    
    def complete(self):
        """Mark the order as completed."""
        self.is_completed = True
    
    def get_summary(self):
        """Get a summary of the order."""
        return {
            "user": self.user.get_display_name(),
            "products": format_product_list(self.products),
            "total": f"${self.get_total():.2f}",
            "status": "Completed" if self.is_completed else "Pending"
        }


def create_order(user, products=None):
    """Create a new order."""
    return Order(user, products)


def process_order(order):
    """Process an order."""
    # Simulate processing logic
    print(f"Processing order for {order.user.get_display_name()}")
    print(f"Total: ${order.get_total():.2f}")
    
    # Mark as completed
    order.complete()
    
    return order
