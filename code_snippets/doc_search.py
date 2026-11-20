import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv() #by default looks for .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

EMBED_MODEL = os.getenv("EMBED_MODEL")
KB_FOLDER = os.getenv("KB_FOLDER")

# Get the embedding of a text from Embedding model
def get_embedding(text):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding

# Get the cosine similarity between two vectors
def cosine_similarity(A, B):
    dot_prod = np.dot(A, B)
    norm_a = np.linalg.norm(A)
    norm_b = np.linalg.norm(B)
    return dot_prod / (norm_a * norm_b)

def load_documents(folder=KB_FOLDER):
    documents = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue
        
        path = os.path.join(folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            documents.append({
                "source": filename,
                "text": f.read()
            })
    return documents

#Add embeddings to the documents
def add_embeddings(documents):
    for doc in documents:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=doc["text"]
        )
        doc["vector"] = response.data[0].embedding
    return documents

# Search method to search the top k documents for a user query
def search(query, documents, top_k=3):
    query_vector = get_embedding(query)
    
    results = []
    for doc in documents:
        sim = cosine_similarity(query_vector, doc["vector"])
        results.append({
            "score": float(sim),
            "source": doc["source"],
            "text": doc["text"],
            "size": len(doc["text"])
        })
    
    # Sort by similarity in descending order
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return the top k documents
    return results[:top_k]

#testing method
def test(user_query, documents, top_k=3):
    print(f"\nUser Query: {user_query}\n")

    results = search(user_query, documents, top_k)

    for r in results:
        print(f" {r['score']:.2f} - {r['source']} - {r['size']} characters)")
        

documents = load_documents()
documents = add_embeddings(documents)

print(f"We have embedded {len(documents)} documents from the knowledge base folder '{KB_FOLDER}'.")

user_query = "How many days I will get for maternity leave ?"
test(user_query, documents, top_k=3)