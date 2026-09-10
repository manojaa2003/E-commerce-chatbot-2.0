import os
import re

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from groq import Groq
from langchain_core.messages import AIMessage, HumanMessage
from ecommerce_chatbot.backend_routes.config import settings

load_dotenv()

groq_client = Groq()

def get_connection():
    return psycopg2.connect(
        host=settings.database_hostname,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_username,
        password=settings.database_password,
    )

def run_query(question):
    if question.strip().upper().startswith('SELECT'):
        with get_connection() as conn:
            df = pd.read_sql_query(question, conn)
            return df


def generate_query(question):
    prompt = f'''
        You are an expert in understanding the database schema and generating SQL queries for a natural language question asked
        pertaining to the data you have. The schema is provided in the schema tags. 
        <schema> 
        table: product 
        fields: 
        id - integer (unique product id)
        product_link - string (hyperlink to product)	
        title - string (name of the product)	
        brand - string (brand of the product)	
        price - integer (price of the product in Indian Rupees)	
        discount - float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2, and such.)	
        avg_rating - float (average rating of the product. Range 0-5, 5 is the highest.)	
        total_ratings - integer (total number of ratings for the product)
        </schema>
        Make sure whenever you try to search for the brand name, the name can be in any case add like  LOWER(brand). 
        So, make sure to use %LIKE% to find the brand in condition. Never use "ILIKE". 
        Create a single SQL query for the question provided. 
        The query should have all the fields in SELECT clause (i.e. SELECT *)
        
        Just the SQL query is needed, nothing more. Always provide the SQL in between the <SQL></SQL> tags.
        '''
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.3,
    )

    return chat_completion.choices[0].message.content


def final_answer_generation(question, data):
    final_prompt = f'''
    You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided.
    You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. 
    Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. 
    Just a plain simple natural language response.
    The Data would always be in context to the question asked. 
    
    Question:
    {question}
    
    For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. 
    So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
    There can also be cases where you are given an entire dataframe in the Data: field. 
    Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
    Product title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
    For example:
    1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
    2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
    3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
    '''
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": final_prompt,
            },
            {
                "role": "user",
                "content": f"Question:{question},Data:{data}",
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.3,
    )

    return chat_completion.choices[0].message.content


def sql_chain(state):
    question = state["rewritten_query"]
    sql_query = generate_query(question)
    pattern = "<SQL>(.*?)</SQL>"
    matches = re.findall(pattern, sql_query, re.DOTALL)
    if len(matches) == 0:
        return {"messages": [AIMessage(content="Sorry, LLM is not able to generate query for your question")]}
    print(matches[0])
    response = run_query(matches[0])
    if response is None:
        return {"messages": [AIMessage(content="Sorry there was a problem in executing the query")]}
    response = response[:4]
    final_data = response.to_dict(orient='records')

    final_answer = final_answer_generation(question, final_data)

    return {
        "messages" : [AIMessage(content=final_answer)]
    }


if __name__ == "__main__":
    result = sql_chain('give me shoes under 1k')
    print(result)