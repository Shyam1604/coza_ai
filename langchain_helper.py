from langchain_community.document_loaders import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()  # Take environment variables from .env (especially OpenAI API key)

from langchain_google_genai import GoogleGenerativeAI

# Fetch the API key from the environment
google_api_key = st.secrets["GOOGLE_API_KEY"]

# Initialize the LLM (GoogleGenerativeAI)
llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api_key, temperature=0.6)

# Initialize Hugging Face embeddings
# embeddings = HuggingFaceEmbeddings()
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # or another small, supported model

# Path to save/load the FAISS vector database
vectordb_file_path = "vector_database"

def create_vector_db():
    try:
        # Load data from the CSV file
        loader = CSVLoader(file_path='Fashion sense.csv', source_column="Input")
        data = loader.load()

        # Create the FAISS vector store with embeddings
        vectordb = FAISS.from_documents(documents=data, embedding=embeddings)

        # Save the FAISS vector database locally
        vectordb.save_local(vectordb_file_path)
        print("Vector database saved successfully.")

    except Exception as e:
        print(f"Error while saving vector database: {e}")

def get_qa_chain():
    try:
        # Load the vector database from the local directory
        vectordb = FAISS.load_local(vectordb_file_path, embeddings, allow_dangerous_deserialization=True)

        # Create a retriever with a score threshold
        retriever = vectordb.as_retriever(score_threshold=0.7)

        # Define the prompt template for the fashion recommendation chatbot
        prompt_template = """
    You are a highly knowledgeable fashion sense recommendation chatbot. Your job is to provide fashion advice based on user preferences, questions, and context.

    INSTRUCTIONS:
    1. **Fashion-Focused Response:**
    - Your primary focus is on providing recommendations related to fashion, style advice, outfit combinations, body-type-specific suggestions, and current trends.
    - Answer only fashion-related questions. If a question is unrelated to fashion, respond politely and inform the user that you can only assist with fashion-related queries.

    2. **Comprehensive Fashion Advice:**
    - Offer tailored outfit suggestions considering factors such as style, occasion, weather, body type, color preferences, and current trends.
    - Provide multiple outfit options when relevant, and include specific details such as clothing types, fabric choices, color combinations, and accessories.
    - If applicable, recommend seasonal or occasion-specific clothing, such as summer dresses, office wear, formal attire, casual outfits, or winter essentials.

    3. **User Preferences:**
    - Consider user input regarding style, color, body type, and occasion to personalize your advice.
    - For example, if the user mentions their body type (athletic, curvy, petite, etc.), offer recommendations that complement their figure.

    4. **Out-of-Domain Responses:**
    - If the question is not related to fashion, respond with: "Sorry, I don't know. I specialize in fashion advice. Please feel free to ask me about outfits, style tips, or other fashion-related topics."
    - Avoid answering non-fashion-related questions, and guide users back to fashion topics.

    5. **Polite and Friendly Tone:**
    - Always maintain a polite and friendly tone in your responses, whether providing advice or politely declining to answer non-fashion-related questions.

    EXAMPLES:
    1. *Fashion-Related*: "What should I wear to a beach wedding?"
    - "For a beach wedding, you could go for a flowy maxi dress in light fabrics like chiffon or cotton. Pair it with wedge sandals and delicate accessories. Opt for light colors such as pastels or floral prints to match the beach vibe."

    2. *Non-Fashion-Related*: "Can you tell me the capital of France?"
    - "Sorry, I don't know. I specialize in fashion advice. Please feel free to ask me about outfits, style tips, or other fashion-related topics."

    CONTEXT:
    {context}

    QUESTION:
    {question}
    """

        # Create a prompt template
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        # Create a retrieval-based QA chain
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            input_key="query",
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        return chain

    except Exception as e:
        print(f"Error while creating QA chain: {e}")

# Ensure the correct entry point
if __name__ == "__main__":
    create_vector_db()
    chain = get_qa_chain()
    print("Process completed successfully.")
