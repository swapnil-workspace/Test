# In chatgpt_integration.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()

class ChatGPTIntegration:
    def __init__(self, model="gpt-3.5-turbo"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.project_id = os.getenv("OPENAI_PROJECT_ID")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        openai.api_key = self.api_key
        if self.project_id:
            openai.project_id = self.project_id
            print(f"ChatGPT client initialized with Project ID: {self.project_id}")
        else:
            print("ChatGPT client initialized without Project ID.")
            
        self.model = model

    def get_response(self, user_query, conversation_history=None):
        # ... (existing general query handling) ...
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_query})

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except openai.AuthenticationError:
            return "Authentication failed. Please check your OpenAI API key."
        except openai.APITimeoutError:
            return "The request timed out. Please try again."
        except openai.APIConnectionError as e:
            return f"Could not connect to OpenAI API: {e}"
        except openai.APIStatusError as e:
            return f"OpenAI API returned an error: {e.status_code} - {e.response}"
        except Exception as e:
            return f"An unexpected error occurred with ChatGPT: {e}"

    def classify_intent_with_llm(self, user_query, intents=["Product_Query", "General_Query"]):
        system_message = (
            "You are an intent classification expert. "
            "Your task is to analyze user queries and identify their primary intent. "
            "The only valid intents are: 'Product_Query', 'General_Query'. "
            "If the query asks for specific information about a product (e.g., price, features, description, availability), or mentions a product ID, classify it as 'Product_Query'. "
            "For any other type of query (e.g., greetings, small talk, general knowledge questions, questions about your capabilities), classify it as 'General_Query'. "
            "Respond ONLY with the intent label, followed by nothing else."
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Classify the following user query: '{user_query}'"}
        ]

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=20, # Keep response short
                temperature=0.0, # Make it deterministic for classification
            )
            
            intent = response.choices[0].message.content.strip()
            
            if intent in intents:
                return intent, 1.0 # Assume high confidence if it returns a valid intent
            else:
                # Fallback if LLM gives an unexpected output (e.g., hallucinates a new intent)
                print(f"Warning: LLM returned unexpected intent '{intent}'. Defaulting to General_Query.")
                return "General_Query", 0.0

        except Exception as e:
            print(f"Error classifying intent with LLM: {e}")
            return "General_Query", 0.0 # Fallback in case of API error
