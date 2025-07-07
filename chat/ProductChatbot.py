from product_data import ProductKnowledgeBase
from chatgpt_integration import ChatGPTIntegration
import re

class ProductChatbot:
    def __init__(self, json_file_path, chatgpt_model="gpt-3.5-turbo"):
        self.product_kb = ProductKnowledgeBase(json_file_path)
        self.chat_gpt = ChatGPTIntegration(model=chatgpt_model)
        self.conversation_history = []
        print("Chatbot initialized. Type 'exit' to quit.")

    def _is_product_query(self, user_query):
        # Simple keyword-based intent recognition
        keywords = ["product", "details", "info", "price", "features", "availability", "id", "what about"]
        query_lower = user_query.lower()
        
        # Check for direct product ID query (e.g., "PROD001 details")
        if re.search(r'\b(prod\d{3})\b', query_lower):
            return True

        for keyword in keywords:
            if keyword in query_lower:
                return True
        return False

    def _handle_product_query(self, user_query):
        # Try to extract a product ID first
        match = re.search(r'\b(prod\d{3})\b', user_query.lower())
        if match:
            product_id = match.group(1).upper() # Ensure ID is uppercase for lookup
            product = self.product_kb.get_product_details_by_id(product_id)
            if product:
                return self.product_kb.format_product_details(product)
            else:
                return f"I couldn't find a product with ID '{product_id}'. Please check the ID and try again."

        # If no specific ID, try to search by name/keywords
        results = self.product_kb.search_products(user_query)
        if results:
            if len(results) == 1:
                return self.product_kb.format_product_details(results[0])
            else:
                names = [p.get('name', 'Unknown Product') for p in results]
                return f"I found multiple products: {', '.join(names)}. Can you please be more specific or provide a product ID?"
        else:
            return "I couldn't find product information related to your query in my database. Perhaps you're looking for something else?"

    def _update_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
        # Keep history short to avoid exceeding token limits for LLM
        if len(self.conversation_history) > 10: # Keep last 10 messages (5 turns)
            self.conversation_history = self.conversation_history[-10:]

    def chat(self):
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Chatbot: Goodbye!")
                break

            self._update_history("user", user_input)

            if self._is_product_query(user_input):
                response = self._handle_product_query(user_input)
                print(f"Chatbot: {response}")
                self._update_history("assistant", response)
            else:
                # Fallback to ChatGPT for general queries
                response = self.chat_gpt.get_response(user_input, self.conversation_history)
                print(f"Chatbot: {response}")
                self._update_history("assistant", response)

# Run the chatbot
if __name__ == "__main__":
    # Ensure products.json is in the same directory or provide the full path
    chatbot = ProductChatbot("products.json") 
    chatbot.chat()
