import json
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from chatgpt_integration import ChatGPTIntegration # Import your ChatGPTIntegration

class ProductKnowledgeBase:
    def __init__(self, json_file_path, embedding_model_instance, persist_directory="./chroma_db"):
        self.json_file_path = json_file_path
        self.embedding_model = embedding_model_instance # Use the embeddings from ChatGPTIntegration
        self.persist_directory = persist_directory
        self.vector_db = None
        self._load_and_process_products()

    def _load_and_process_products(self):
        """Loads products from JSON, converts them to documents, chunks them, and embeds into ChromaDB."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Product JSON file not found at {self.json_file_path}")
            return
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {self.json_file_path}")
            return

        documents = []
        for product in products_data:
            # Create a comprehensive string representation of each product
            product_text = f"Product ID: {product.get('product_id', 'N/A')}\n" \
                           f"Name: {product.get('name', 'N/A')}\n" \
                           f"Category: {product.get('category', 'N/A')}\n" \
                           f"Price: ${product.get('price', 'N/A'):.2f}\n" \
                           f"Description: {product.get('description', 'N/A')}\n" \
                           f"Features: {', '.join(product.get('features', []))}\n" \
                           f"Availability: {product.get('availability', 'N/A')}\n" \
                           f"Rating: {product.get('rating', 'N/A')}/5"
            
            # Add product_id to metadata for easier lookup later
            documents.append(Document(page_content=product_text, metadata={"product_id": product.get("product_id")}))

        # Chunk the documents (important for larger documents, less critical for small products)
        # Even for small chunks, it's good practice.
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        print(f"Loaded {len(products_data)} products and split into {len(chunks)} chunks.")

        # Initialize and populate ChromaDB
        # This will create or load the database in self.persist_directory
        self.vector_db = Chroma.from_documents(
            chunks,
            self.embedding_model,
            persist_directory=self.persist_directory
        )
        print(f"ChromaDB initialized and populated at {self.persist_directory}")

    def get_relevant_product_info(self, query, k=3):
        """
        Performs a similarity search in the vector database to retrieve relevant product information.
        Returns a list of Document objects.
        """
        if not self.vector_db:
            print("Error: Vector database not initialized.")
            return []
        
        # Perform similarity search
        retrieved_docs = self.vector_db.similarity_search(query, k=k)
        print(f"Retrieved {len(retrieved_docs)} documents for query: '{query}'")
        return retrieved_docs

# Example usage (for testing)
if __name__ == "__main__":
    chat_gpt_integrator = ChatGPTIntegration()
    product_kb = ProductKnowledgeBase("data/products.json", chat_gpt_integrator.get_embedding_model())

    query = "What are the features of the Eco-Friendly Water Bottle?"
    relevant_info = product_kb.get_relevant_product_info(query)
    for doc in relevant_info:
        print("\n--- Retrieved Document ---")
        print(doc.page_content)
        print(f"Metadata: {doc.metadata}")

    query = "Tell me about the smart home hub."
    relevant_info = product_kb.get_relevant_product_info(query)
    for doc in relevant_info:
        print("\n--- Retrieved Document ---")
        print(doc.page_content)
        print(f"Metadata: {doc.metadata}")
