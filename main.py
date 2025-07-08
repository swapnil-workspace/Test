from chatbot import ProductChatbot

if __name__ == "__main__":
    # Ensure your data/products.json exists
    # Ensure your .env file with OPENAI_API_KEY is configured

    # Initialize the chatbot
    # You can customize model names and paths here if needed
    bot = ProductChatbot(
        json_file_path="data/products.json",
        chatgpt_llm_model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
        chatgpt_embedding_model="text-embedding-ada-002", # Or "text-embedding-3-small"
        chroma_db_path="./chroma_db"
    )

    # Start the chat loop
    bot.chat_loop()
