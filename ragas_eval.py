import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from ragas.llms import LangchainLLM
from ragas.embeddings import LangchainEmbeddings
from chatgpt_integration import ChatGPTIntegration
from product_knowledge_base import ProductKnowledgeBase
from langchain_core.documents import Document

# Initialize OpenAI components
chat_gpt_integrator = ChatGPTIntegration()
eval_llm = LangchainLLM(llm=chat_gpt_integrator.get_llm_for_rag())
eval_embeddings = LangchainEmbeddings(embeddings=chat_gpt_integrator.get_embedding_model())

# Override default Ragas LLM/Embeddings if needed
# faithfulness.llm = eval_llm
# answer_relevancy.llm = eval_llm
# context_recall.llm = eval_llm
# context_precision.llm = eval_llm
# faithfulness.embeddings = eval_embeddings
# answer_relevancy.embeddings = eval_embeddings
# context_recall.embeddings = eval_embeddings
# context_precision.embeddings = eval_embeddings


def run_ragas_evaluation(test_data_path="ragas_test_data.csv"):
    """
    Runs Ragas evaluation on your RAG pipeline.
    
    Args:
        test_data_path (str): Path to a CSV file containing test data.
                              Columns must include: 'question', 'ground_truth', 'expected_contexts'
                              'expected_contexts' should be a list of strings representing ideal retrieved chunks.
                              Example format:
                              question,ground_truth,expected_contexts
                              "What is the price of P001?", "The price of the Eco-Friendly Water Bottle (P001) is $19.99.", "['Product ID: P001\nName: Eco-Friendly Water Bottle\nCategory: Hydration\nPrice: $19.99...']"
    """
    try:
        test_df = pd.read_csv(test_data_path)
        # Ensure expected_contexts column is parsed as list of strings
        test_df['expected_contexts'] = test_df['expected_contexts'].apply(eval) # Danger: eval() can be unsafe. Use literal_eval if possible.

    except FileNotFoundError:
        print(f"Error: Ragas test data file not found at {test_data_path}.")
        print("Please create 'ragas_test_data.csv' with 'question', 'ground_truth', 'expected_contexts' columns.")
        return
    except Exception as e:
        print(f"Error loading or parsing test data: {e}")
        return

    # Initialize your product knowledge base (this will load and embed your products)
    product_kb = ProductKnowledgeBase("data/products.json", chat_gpt_integrator.get_embedding_model())
    
    # Prepare the dataset for Ragas evaluation
    # This involves running each question through your RAG pipeline
    # and collecting the generated answer and retrieved contexts.
    
    data_for_ragas = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    # Simulate your RAG pipeline's behavior for each test question
    for index, row in test_df.iterrows():
        question = row["question"]
        ground_truth = row["ground_truth"]
        expected_contexts = row["expected_contexts"] # Use for context_recall metric

        # Simulate retrieval
        retrieved_docs_langchain = product_kb.get_relevant_product_info(question, k=5) # Retrieve more docs for better recall chance
        retrieved_contexts_str = [doc.page_content for doc in retrieved_docs_langchain]

        # Simulate generation using the RAG chain (similar to chatbot.py)
        rag_prompt_template_eval = ChatPromptTemplate.from_messages(
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
        rag_chain_eval = (
            {"context": lambda q: retrieved_docs_langchain, "query": RunnablePassthrough()}
            | rag_prompt_template_eval
            | chat_gpt_integrator.get_llm_for_rag()
            | StrOutputParser()
        )
        generated_answer = rag_chain_eval.invoke(question)

        data_for_ragas["question"].append(question)
        data_for_ragas["answer"].append(generated_answer)
        data_for_ragas["contexts"].append(retrieved_contexts_str)
        data_for_ragas["ground_truth"].append(ground_truth)
        
    ragas_dataset = Dataset.from_dict(data_for_ragas)

    print("\nStarting Ragas evaluation...")
    result = evaluate(
        ragas_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        ],
        llm=eval_llm,
        embeddings=eval_embeddings
    )

    print("\nRagas Evaluation Results:")
    print(result)

    # Convert results to DataFrame for better viewing
    result_df = result.to_dataframe()
    print("\nDetailed Ragas Results (DataFrame):")
    print(result_df)

if __name__ == "__main__":
    # Create a dummy ragas_test_data.csv for demonstration
    # In a real scenario, you'd populate this with your actual test cases
    dummy_ragas_data = """question,ground_truth,expected_contexts
What is the price of the Eco-Friendly Water Bottle?,The Eco-Friendly Water Bottle (P001) costs $19.99.,["Product ID: P001\\nName: Eco-Friendly Water Bottle\\nCategory: Hydration\\nPrice: $19.99\\nDescription: A durable, insulated water bottle made from recycled materials. Keeps drinks cold for 24 hours and hot for 12 hours. Capacity: 750ml.\\nFeatures: BPA-free, Double-wall insulation, Leak-proof cap, Wide mouth for ice\\nAvailability: In Stock\\nRating: 4.8/5"]
Tell me about the Smart Home Hub.,The Smart Home Hub (P002) allows you to centralize control of smart home devices, is compatible with Alexa, Google Assistant, and Apple HomeKit, and supports Zigbee & Z-Wave.,["Product ID: P002\\nName: Smart Home Hub\\nCategory: Electronics\\nPrice: $99.99\\nDescription: Centralize control of your smart home devices. Compatible with Alexa, Google Assistant, and Apple HomeKit. Requires Wi-Fi.\\nFeatures: Voice control, App control, Zigbee & Z-Wave compatible, Secure encryption\\nAvailability: Low Stock\\nRating: 4.5/5"]
Is the Wireless Ergonomic Keyboard in stock?,No, the Wireless Ergonomic Keyboard (P003) is currently Out of Stock.,["Product ID: P003\\nName: Wireless Ergonomic Keyboard\\nCategory: Peripherals\\nPrice: $75.00\\nDescription: Designed for comfort and efficiency, reducing strain during long typing sessions. Includes a detachable wrist rest. Connects via Bluetooth.\\nFeatures: Split ergonomic design, Quiet keys, Rechargeable battery, Multi-device connectivity\\nAvailability: Out of Stock\\nRating: 4.2/5"]
What is the battery life of the Portable Bluetooth Speaker?,The Portable Bluetooth Speaker (P004) has a 10-hour battery life.,["Product ID: P004\\nName: Portable Bluetooth Speaker\\nCategory: Audio\\nPrice: $49.99\\nDescription: Compact and powerful speaker with rich bass and clear highs. Ideal for outdoor adventures. IPX7 waterproof.\\nFeatures: 10-hour battery life, Built-in microphone, Stereo pairing, USB-C charging\\nAvailability: In Stock\\nRating: 4.7/5"]
Tell me a joke.,I cannot tell jokes as I am a product information chatbot.,[]
"""
    with open("ragas_test_data.csv", "w") as f:
        f.write(dummy_ragas_data)

    run_ragas_evaluation("ragas_test_data.csv")
