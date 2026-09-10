import pandas as pd
import chromadb
from pathlib import Path
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq
import os

from langchain_core.messages import HumanMessage,AIMessage


load_dotenv()

general_qa_path = Path(__file__).parent.parent/"resources/ecommerce_chatbot_qna.csv"
chroma_client = chromadb.Client()
collections_name = "general_qa_client"

groq = Groq()

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
)

def general_data_ingest(path):
    if collections_name not in [collection.name for collection in chroma_client.list_collections()]:
        print("Loading data to Chroma database")
        collections = chroma_client.get_or_create_collection(
            name=collections_name,
            embedding_function=ef,
        )

        df = pd.read_csv(general_qa_path)
        docs = df['question'].tolist()
        metadata = [{"answer" : data} for data in df['answer'].tolist()]

        ids = [f"id_{i}" for i in range(len(docs))]

        collections.add(
            documents = docs,
            metadatas= metadata,
            ids=ids,
        )
        print("Loaded data successfully")
    else:
        print(f"Collection -> {collections_name} already exist")

def query_relevant_answ(query):
    collection = chroma_client.get_collection(
        name=collections_name,
        embedding_function=ef,
    )

    result = collection.query(
        query_texts=query,
        n_results=2,
    )
    return result

def generate_answer(query,context):
    prompt = f'''
    Given the following context, question, generate answer based on these elements only.
    If the answer is not found in the context, kindly state "I don't know". Don't try to make up an answer.
    
    Question:
    {query}
    
    Context:
    {context}
    '''
    chat_completion = groq.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=os.environ['GROQ_MODEL'],
    )
    return chat_completion.choices[0].message.content

def general_qa_chain(state):
    general_data_ingest(general_qa_path)
    query = state["rewritten_query"]
    queried_answers = query_relevant_answ(query)
    context = " ".join(answ.get('answer') for answ in queried_answers['metadatas'][0])
    answer = generate_answer(
        query,
        context,
    )
    return {
        "messages" : [AIMessage(content=answer)]
    }

if __name__ == "__main__":
    print(general_data_ingest.__name__)
    query1 = "what is your role"
    print(general_qa_chain(query1))