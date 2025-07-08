import openai
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

class ChatGPTIntegration:
    def __init__(self, llm_model="gpt-3.5-turbo", embedding_model="text-embedding-ada-002"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.project_id = os.getenv("OPENAI_PROJECT_ID")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        # Initialize OpenAI client directly for non-LangChain calls if needed, though LangChain handles it well
        # openai.api_key = self.api_key
        # if self.project_id:
        #     openai.project_id = self.project_id
        #     print(f"ChatGPT client initialized with Project ID: {self.project_id}")
        # else:
        #     print("ChatGPT client initialized without Project ID.")
            
        # LangChain LLM for chat responses
        self.llm = ChatOpenAI(model=llm_model, temperature=0.7, openai_api_key=self.api_key, openai_project_id=self.project_id)
        
        # LangChain Embeddings for vector database
        self.embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=self.api_key, openai_project_id=self.project_id)

    def get_llm_for_rag(self):
        """Returns the LangChain LLM instance for RAG chain."""
        return self.llm

    def get_embedding_model(self):
        """Returns the LangChain Embedding model instance."""
        return self.embeddings

    def get_chat_response(self, user_query, conversation_history=None):
        """
        Generates a general chat response using the LLM.
        `conversation_history` should be a list of LangChain message objects (SystemMessage, HumanMessage, AIMessage).
        """
        messages = [SystemMessage(content="You are a helpful assistant.")]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append(HumanMessage(content=user_query))

        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"An error occurred while getting a general response: {e}"

    def classify_intent_with_llm(self, user_query, intents=["Product_Query", "General_Query"]):
        """
        Classifies user intent using the LLM in a zero-shot manner.
        Returns the predicted intent and a dummy confidence.
        """
        system_message = (
            "You are an intent classification expert. "
            "Your task is to analyze user queries and identify their primary intent. "
            f"The only valid intents are: {', '.join(intents)}. "
            "If the query asks for specific information about a product (e.g., price, features, description, availability, product ID), "
            "classify it as 'Product_Query'. "
            "For any other type of query (e.g., greetings, small talk, general knowledge questions, questions about your capabilities), "
            "classify it as 'General_Query'. "
            "Respond ONLY with the exact intent label, followed by nothing else."
        )

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=f"Classify the following user query: '{user_query}'")
        ]

        try:
            # Use a very low temperature for deterministic classification
            classification_llm = ChatOpenAI(model=self.llm.model_name, temperature=0.0, openai_api_key=self.api_key, openai_project_id=self.project_id)
            response = classification_llm.invoke(messages)
            
            intent = response.content.strip()
            
            if intent in intents:
                return intent, 1.0 # Assume high confidence if it returns a valid intent
            else:
                print(f"Warning: LLM returned unexpected intent '{intent}' for query '{user_query}'. Defaulting to General_Query.")
                return "General_Query", 0.0

        except Exception as e:
            print(f"Error classifying intent with LLM: {e}")
            return "General_Query", 0.0 # Fallback in case of API error
