import json

class ProductKnowledgeBase:
    def __init__(self, json_file_path):
        self.products = self._load_products(json_file_path)

    def _load_products(self, json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: JSON file not found at {json_file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {json_file_path}")
            return []

    def search_products(self, query):
        results = []
        query_lower = query.lower()

        for product in self.products:
            # Simple keyword matching across various fields
            if (query_lower in product.get("name", "").lower() or
                query_lower in product.get("category", "").lower() or
                query_lower in product.get("description", "").lower() or
                any(query_lower in f.lower() for f in product.get("features", []))):
                results.append(product)
        return results

    def get_product_details_by_id(self, product_id):
        for product in self.products:
            if product.get("id") == product_id:
                return product
        return None

    def format_product_details(self, product):
        if not product:
            return "I couldn't find details for that product."

        details = f"Product: {product.get('name', 'N/A')} (ID: {product.get('id', 'N/A')})\n"
        details += f"Category: {product.get('category', 'N/A')}\n"
        details += f"Price: ${product.get('price', 'N/A'):.2f}\n"
        details += f"Description: {product.get('description', 'N/A')}\n"
        if product.get('features'):
            details += f"Features: {', '.join(product['features'])}\n"
        details += f"Availability: {product.get('availability', 'N/A')}"
        return details

# Example Usage (for testing the class)
if __name__ == "__main__":
    kb = ProductKnowledgeBase("products.json")
    print("All products loaded:", len(kb.products))

    # Test search
    search_query = "water bottle"
    found_products = kb.search_products(search_query)
    print(f"\nSearching for '{search_query}':")
    if found_products:
        for p in found_products:
            print(kb.format_product_details(p))
    else:
        print("No products found.")

    # Test by ID
    product_id = "PROD001"
    product = kb.get_product_details_by_id(product_id)
    print(f"\nDetails for product ID {product_id}:")
    print(kb.format_product_details(product))
