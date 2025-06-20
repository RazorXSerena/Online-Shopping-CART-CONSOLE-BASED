import json
from typing import Dict


class Product:
    def __init__(self, product_id: str, name: str, price: float, quantity_available: int):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_available = quantity_available

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def quantity_available(self) -> int:
        return self._quantity_available

    @quantity_available.setter
    def quantity_available(self, value: int) -> None:
        if value >= 0:
            self._quantity_available = value
        else:
            raise ValueError("Quantity cannot be negative")

    def decrease_quantity(self, amount: int) -> bool:
        if amount <= 0 or amount > self._quantity_available:
            return False
        self._quantity_available -= amount
        return True

    def increase_quantity(self, amount: int) -> None:
        if amount > 0:
            self._quantity_available += amount
        else:
            raise ValueError("Amount must be positive")

    def display_details(self) -> str:
        return (f"Product ID: {self._product_id}\n"
                f"Name: {self._name}\n"
                f"Price: ${self._price:.2f}\n"
                f"Available Quantity: {self._quantity_available}")

    def to_dict(self) -> dict:
        return {
            'type': 'product',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_available': self._quantity_available
        }

    def __str__(self) -> str:
        return f"{self._name} (ID: {self._product_id}) - ${self._price:.2f}"


class PhysicalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float,
                 quantity_available: int, weight: float):
        super().__init__(product_id, name, price, quantity_available)
        self._weight = weight

    @property
    def weight(self) -> float:
        return self._weight

    def display_details(self) -> str:
        return (super().display_details() +
                f"\nWeight: {self._weight} kg")

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            'type': 'physical',
            'weight': self._weight
        })
        return base_dict

    def __str__(self) -> str:
        return f"{super().__str__()} (Physical, {self._weight}kg)"


class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float,
                 quantity_available: int, download_link: str):
        super().__init__(product_id, name, price, quantity_available)
        self._download_link = download_link

    @property
    def download_link(self) -> str:
        return self._download_link

    def display_details(self) -> str:
        return (super().display_details() +
                f"\nDownload Link: {self._download_link}")

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            'type': 'digital',
            'download_link': self._download_link
        })
        return base_dict

    def __str__(self) -> str:
        return f"{super().__str__()} (Digital)"


class CartItem:
    def __init__(self, product: Product, quantity: int):
        self._product = product
        self._quantity = quantity

    @property
    def product(self) -> Product:
        return self._product

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        if value >= 0:
            self._quantity = value
        else:
            raise ValueError("Quantity cannot be negative")

    def calculate_subtotal(self) -> float:
        return self._product.price * self._quantity

    def __str__(self) -> str:
        return (f"Item: {self._product.name}, "
                f"Quantity: {self._quantity}, "
                f"Price: ${self._product.price:.2f}, "
                f"Subtotal: ${self.calculate_subtotal():.2f}")

    def to_dict(self) -> dict:
        return {
            'product_id': self._product.product_id,
            'quantity': self._quantity
        }


class ShoppingCart:
    def __init__(self, product_catalog_file: str = 'products.json',
                 cart_state_file: str = 'cart.json'):
        self._items: Dict[str, CartItem] = {}
        self._product_catalog_file = product_catalog_file
        self._cart_state_file = cart_state_file
        self._product_catalog = self._load_catalog()
        self._load_cart_state()

    def _load_catalog(self) -> Dict[str, Product]:
        try:
            with open(self._product_catalog_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            return {}

        catalog = {}
        for product_id, product_data in data.items():
            product_type = product_data.get('type', 'product')

            if product_type == 'physical':
                product = PhysicalProduct(
                    product_id=product_data['product_id'],
                    name=product_data['name'],
                    price=product_data['price'],
                    quantity_available=product_data['quantity_available'],
                    weight=product_data['weight']
                )
            elif product_type == 'digital':
                product = DigitalProduct(
                    product_id=product_data['product_id'],
                    name=product_data['name'],
                    price=product_data['price'],
                    quantity_available=product_data['quantity_available'],
                    download_link=product_data['download_link']
                )
            else:
                product = Product(
                    product_id=product_data['product_id'],
                    name=product_data['name'],
                    price=product_data['price'],
                    quantity_available=product_data['quantity_available']
                )

            catalog[product_id] = product

        return catalog

    def _load_cart_state(self) -> None:
        try:
            with open(self._cart_state_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            return

        for item_data in data.values():
            product_id = item_data['product_id']
            quantity = item_data['quantity']

            if product_id in self._product_catalog:
                product = self._product_catalog[product_id]
                self._items[product_id] = CartItem(product, quantity)

    def _save_catalog(self) -> None:
        catalog_dict = {
            product_id: product.to_dict()
            for product_id, product in self._product_catalog.items()
        }
        with open(self._product_catalog_file, 'w') as file:
            json.dump(catalog_dict, file, indent=2)

    def _save_cart_state(self) -> None:
        cart_dict = {
            product_id: item.to_dict()
            for product_id, item in self._items.items()
        }
        with open(self._cart_state_file, 'w') as file:
            json.dump(cart_dict, file, indent=2)

    def add_item(self, product_id: str, quantity: int) -> bool:
        if product_id not in self._product_catalog:
            return False

        product = self._product_catalog[product_id]

        if not product.decrease_quantity(quantity):
            return False

        if product_id in self._items:
            self._items[product_id].quantity += quantity
        else:
            self._items[product_id] = CartItem(product, quantity)

        self._save_cart_state()
        return True

    def remove_item(self, product_id: str) -> bool:
        if product_id not in self._items:
            return False

        item = self._items[product_id]
        item.product.increase_quantity(item.quantity)
        del self._items[product_id]

        self._save_cart_state()
        return True

    def update_quantity(self, product_id: str, new_quantity: int) -> bool:
        if product_id not in self._items or new_quantity < 0:
            return False

        item = self._items[product_id]
        product = item.product
        quantity_diff = new_quantity - item.quantity

        if quantity_diff > 0:
            if not product.decrease_quantity(quantity_diff):
                return False
        elif quantity_diff < 0:
            product.increase_quantity(-quantity_diff)

        item.quantity = new_quantity

        if new_quantity == 0:
            del self._items[product_id]

        self._save_cart_state()
        return True

    def get_total(self) -> float:
        return sum(item.calculate_subtotal() for item in self._items.values())

    def display_cart(self) -> None:
        if not self._items:
            print("Your shopping cart is empty.")
            return

        print("\n=== Shopping Cart ===")
        for item in self._items.values():
            print(item)
        print(f"\nGrand Total: ${self.get_total():.2f}\n")

    def display_products(self) -> None:
        if not self._product_catalog:
            print("No products available.")
            return

        print("\n=== Available Products ===")
        for product in self._product_catalog.values():
            print("\n" + product.display_details())
        print()

    def run(self) -> None:
        while True:
            print("\n=== Online Shopping Cart ===")
            print("1. View Products")
            print("2. Add Item to Cart")
            print("3. View Cart")
            print("4. Update Quantity")
            print("5. Remove Item")
            print("6. Checkout (Dummy)")
            print("7. Exit")

            choice = input("Enter your choice (1-7): ")

            if choice == '1':
                self.display_products()
            elif choice == '2':
                self.display_products()
                product_id = input("Enter product ID to add: ")
                try:
                    quantity = int(input("Enter quantity: "))
                    if quantity <= 0:
                        print("Quantity must be positive.")
                        continue
                    if self.add_item(product_id, quantity):
                        print("Item added to cart successfully!")
                    else:
                        print("Failed to add item. Check product ID or available quantity.")
                except ValueError:
                    print("Invalid quantity. Please enter a number.")
            elif choice == '3':
                self.display_cart()
            elif choice == '4':
                self.display_cart()
                if self._items:
                    product_id = input("Enter product ID to update: ")
                    try:
                        new_quantity = int(input("Enter new quantity: "))
                        if new_quantity < 0:
                            print("Quantity cannot be negative.")
                            continue
                        if self.update_quantity(product_id, new_quantity):
                            print("Quantity updated successfully!")
                        else:
                            print("Failed to update quantity. Check product ID or available quantity.")
                    except ValueError:
                        print("Invalid quantity. Please enter a number.")
            elif choice == '5':
                self.display_cart()
                if self._items:
                    product_id = input("Enter product ID to remove: ")
                    if self.remove_item(product_id):
                        print("Item removed successfully!")
                    else:
                        print("Product not found in cart.")
            elif choice == '6':
                total = self.get_total()
                if total > 0:
                    print(f"\n=== Checkout ===")
                    print(f"Total amount: ${total:.2f}")
                    print("Thank you for your purchase!")
                    self._items = {}
                    self._save_cart_state()
                else:
                    print("Your cart is empty. Nothing to checkout.")
            elif choice == '7':
                print("Thank you for shopping with us!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")


def initialize_sample_data():

    catalog = {
        'p1': PhysicalProduct('p1', 'Wireless Mouse', 25.99, 50, 0.2),
        'p2': PhysicalProduct('p2', 'Bluetooth Keyboard', 45.50, 30, 0.5),
        'd1': DigitalProduct('d1', 'E-book: Python Basics', 19.99, 1000, 'https://example.com/download/d1'),
        'd2': DigitalProduct('d2', 'Photo Editing Software', 59.99, 500, 'https://example.com/download/d2'),
        'p3': Product('p3', 'USB Flash Drive 64GB', 12.99, 100)
    }


    catalog_dict = {
        product_id: product.to_dict()
        for product_id, product in catalog.items()
    }
    with open('products.json', 'w') as file:
        json.dump(catalog_dict, file, indent=2)


if __name__ == "__main__":


    cart = ShoppingCart()
    cart.run()