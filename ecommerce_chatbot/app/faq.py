from pathlib import Path
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os
from groq import Groq

from langchain_core.messages import HumanMessage,AIMessage

load_dotenv()

faq_path = Path(__file__).parent.parent/"resources/faq_data.csv"
chroma_client = chromadb.Client()
collection_faq_name =  "faqs"
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
)

groq_client = Groq()

def ingest_faq_data(path):
    if collection_faq_name not in [collection.name for collection in chroma_client.list_collections()]:
        print("adding data to collections")
        collections = chroma_client.get_or_create_collection(
            name=collection_faq_name,
            embedding_function=ef,
        )
        df = pd.read_csv(path)
        docs = df["question"].tolist()
        metadata = [{'answer': ans} for ans in df["answer"].tolist()]
        ids = [f"id_{i}" for i in range(len(docs))]

        collections.add(
            documents= docs,
            metadatas = metadata,
            ids = ids,
        )
        print("data successfully ingested")
    else:
        print(f"{collection_faq_name} already exist")

def get_relevant_qa(query):
    collections = chroma_client.get_collection(
        name=collection_faq_name,
        embedding_function=ef,
    )
    result = collections.query(
        query_texts=[query],
        n_results=2,
    )
    return result

def generate_answer(query,context):
    prompt = f'''
    Given the following context and question, generate answer based on this context only.
    If the answer is not found in the context, kindly state "I don't know". Don't try to make up an answer.
    Question:
    {query}
    
    Context:
    {context}
    '''
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=os.environ['GROQ_FAST'],
    )

    return chat_completion.choices[0].message.content

def faq_chain(state):
    ingest_faq_data(faq_path)
    query = state["rewritten_query"]
    result = get_relevant_qa(query)
    context = " ".join(r.get('answer') for r in result['metadatas'][0])
    answer = generate_answer(query,context)

    return {
        "messages" : [AIMessage(content=answer)]
    }

if __name__ == "__main__":
    ingest_faq_data(faq_path)
    query = "will you accept the cash"
    answer = faq_chain(query)
    print(answer)