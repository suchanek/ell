"""
Models module containing data models for the application.
"""

class User:
    """User model representing a user in the system."""
    
    def __init__(self, name, email, age=None):
        """Initialize a new User instance."""
        self.name = name
        self.email = email
        self.age = age
    
    def get_display_name(self):
        """Return the display name for the user."""
        return f"{self.name} <{self.email}>"
    
    def is_adult(self):
        """Check if the user is an adult (age >= 18)."""
        return self.age is not None and self.age >= 18


class Admin(User):
    """Admin model representing an administrator in the system."""
    
    def __init__(self, name, email, department, age=None):
        """Initialize a new Admin instance."""
        super().__init__(name, email, age)
        self.department = department
    
    def get_display_name(self):
        """Return the display name for the admin."""
        return f"{self.name} ({self.department}) <{self.email}>"


class Product:
    """Product model representing a product in the system."""
    
    def __init__(self, name, price, description=None):
        """Initialize a new Product instance."""
        self.name = name
        self.price = price
        self.description = description
    
    def get_display_price(self):
        """Return the formatted price for display."""
        return f"${self.price:.2f}"
