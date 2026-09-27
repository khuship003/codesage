import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Connect to the same embedding function and database we built in embed.py
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="codesage_chunks",
    embedding_function=embedding_function
)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def ask(question, n_results=3):
    # Step 1: find the most relevant chunks for this question
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )

    retrieved_chunks = results["documents"][0]
    retrieved_files = [meta["file"] for meta in results["metadatas"][0]]

    # Step 2: build a prompt that includes those chunks as context
    context = "\n\n---\n\n".join(retrieved_chunks)
    prompt = f"""You are a helpful assistant answering questions about a codebase.
Use the following code context to answer the question. If the answer isn't in the context, say so.

CONTEXT:
{context}

QUESTION:
{question}
"""

    # Step 3: send it to Groq
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    print("Answer:\n", answer)
    print("\nSources used:", set(retrieved_files))


if __name__ == "__main__":
    while True:
        question = input("\nAsk a question about the codebase (or type 'exit'): ")
        if question.lower() == "exit":
            break
        ask(question)