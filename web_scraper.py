import requests
from bs4 import BeautifulSoup
import json
import faiss
import numpy as np
import openai
import os
from dotenv import load_dotenv

# 🔹 Load OpenAI API Key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def scrape_salon_website(url):
    """Extracts salon details like services, pricing, and FAQs from a given URL."""
    
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("❌ Failed to fetch website:", response.status_code)
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")

    salon_data = {
        "title": soup.title.string.strip() if soup.title else "No title found",
        "services": [],
        "faqs": [],
        "contact_info": "",
    }

    contact_section = soup.find("div", class_="contact") or soup.find("footer")
    if contact_section:
        salon_data["contact_info"] = contact_section.get_text(strip=True)

    # 🔹 Save data to a JSON file
    with open("salon_data.json", "w") as json_file:
        json.dump(salon_data, json_file, indent=4)

    print("✅ Data saved to salon_data.json")
    return salon_data

def get_openai_embedding(text):
    """Generates an embedding vector for the given text using OpenAI's latest API."""
    client = openai.OpenAI()  # Ensure OpenAI client is initialized
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response.data[0].embedding)


def store_in_faiss(data):
    """Stores the scraped text in FAISS after converting it to vectors."""
    texts = [data["title"], data["contact_info"]]
    embeddings = np.array([get_openai_embedding(text) for text in texts])

    dimension = embeddings.shape[1]  # Get the embedding size
    index = faiss.IndexFlatL2(dimension)  # Create FAISS index
    index.add(embeddings)  # Add vectors

    faiss.write_index(index, "salon_faiss.index")  # Save FAISS index
    print("✅ Data stored in FAISS successfully")




if __name__ == "__main__":
    salon_url = "https://www.sallyhershberger.com"  # Replace with a real working salon URL
  # Replace with actual URL
    data = scrape_salon_website(salon_url)
    if data:
        store_in_faiss(data)
import faiss
import numpy as np
import json

# Load FAISS Index & Data
index = faiss.read_index("salon_faiss.index")
with open("salon_data.json", "r") as f:
    salon_data = json.load(f)

def search_faiss(query):
    """Searches FAISS for relevant salon information."""
    if not query.strip():
        return "I couldn't understand your question. Can you rephrase?"

    # Generate embedding for the query
    query_vector = get_openai_embedding(query)
    query_vector = np.array(query_vector).reshape(1, -1).astype("float32")

    # Search FAISS index
    D, I = index.search(query_vector, k=3)  # Get top 3 results

    # Retrieve best-matching text snippets
    responses = []
    for i in I[0]:
        if i != -1:  # ✅ Check for valid index
            index_int = int(i)  # ✅ Convert np.int64 to Python int
            if index_int in salon_data:
                responses.append(salon_data[index_int])

    if responses:
        return " ".join(responses)  # Merge multiple relevant responses
    else:
        return "I couldn't find that information. Would you like me to check available appointments?"
