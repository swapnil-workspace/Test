from chatgpt_integration import ChatGPTIntegration
from product_knowledge_base import ProductKnowledgeBase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class ProductChatbot:
    def __init__(self, json_file_path="data/products.json", chatgpt_llm_model="gpt-3.5-turbo", chatgpt_embedding_model="text-embedding-ada-002", chroma_db_path="./chroma_db", intent_confidence_threshold=0.8):
        self.chat_gpt = ChatGPTIntegration(llm_model=chatgpt_llm_model, embedding_model=chatgpt_embedding_model)
        self.product_kb = ProductKnowledgeBase(json_file_path, self.chat_gpt.get_embedding_model(), persist_directory=chroma_db_path)
        self.conversation_history = []
        self.intent_confidence_threshold = intent_confidence_threshold
        print("Chatbot initialized. Type 'exit' to quit.")

        # Define the RAG prompt template
        self.rag_prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=(
                    "You are a helpful assistant that answers questions about products. "
                    "Use the following retrieved product information to answer the user's question. "
                    "If the product information does not contain the answer, state that you cannot find the information. "
                    "Do not make up information.\n\n"
                    "Retrieved Product Information:\n{context}"
                )),
                HumanMessage(content="{query}")
            ]
        )

        # Create the RAG chain (LangChain Expression Language)
        # This chain will:
        # 1. Take the user query.
        # 2. Retrieve relevant documents using self.product_kb.get_relevant_product_info.
        # 3. Format the retrieved documents as 'context'.
        # 4. Pass 'context' and 'query' to the RAG prompt.
        # 5. Invoke the LLM with the structured prompt.
        # 6. Parse the LLM's output into a string.
        self.rag_chain = (
            {"context": self.product_kb.get_relevant_product_info, "query": RunnablePassthrough()}
            | self.rag_prompt_template
            | self.chat_gpt.get_llm_for_rag()
            | StrOutputParser()
        )

    def _get_intent(self, user_query):
        """
        Uses the LLM to classify the user's intent.
        """
        intent, confidence = self.chat_gpt.classify_intent_with_llm(user_query)
        print(f"Intent classified as: {intent} (Confidence: {confidence:.2f})")
        return intent

    def process_query(self, user_query):
        """
        Main method to process a user query, determine intent, and generate a response.
        """
        intent = self._get_intent(user_query)
        response_text = ""

        if intent == "Product_Query":
            print("Detected Product Query. Initiating RAG...")
            try:
                # Use the RAG chain to get a product-specific response
                response_text = self.rag_chain.invoke(user_query)
                # print(f"RAG Chain Output: {response_text}") # For debugging RAG output
            except Exception as e:
                print(f"Error during RAG processing: {e}")
                response_text = "I encountered an error trying to find product information. Please try again or rephrase your question."
        else:
            print("Detected General Query. Using general LLM chat.")
            # Use the general chat response from ChatGPTIntegration
            # Convert conversation history to LangChain message objects
            lc_history = []
            for msg_type, msg_content in self.conversation_history:
                if msg_type == "human":
                    lc_history.append(HumanMessage(content=msg_content))
                elif msg_type == "ai":
                    lc_history.append(AIMessage(content=msg_content))

            response_text = self.chat_gpt.get_chat_response(user_query, conversation_history=lc_history)

        # Update conversation history
        self.conversation_history.append(("human", user_query))
        self.conversation_history.append(("ai", response_text))
        
        return response_text

    def chat_loop(self):
        """Runs the main chat loop."""
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Chatbot: Goodbye!")
                break
            
            response = self.process_query(user_input)
            print(f"Chatbot: {response}")
