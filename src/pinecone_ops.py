import os

import numpy
from openai import OpenAI
from pinecone import Pinecone

openai_api_key = os.environ.get("OPENAI_API_KEY")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
client = OpenAI(api_key=openai_api_key)
index = Pinecone(api_key=pinecone_api_key).Index("sixthsem")
print(openai_api_key)
print(pinecone_api_key)


def get_embeddings(text):
    return numpy.array(
        client.embeddings.create(input=[text], model="text-embedding-3-small")
        .data[0]
        .embedding
    )


def fetch_from_db(data, user_id):
    total_text = []
    for mapp in data:
        compile = mapp["question"] + "My answer would be- " + mapp["answer"]
        total_text.append(compile)
    return data_preprocessing(total_text, user_id)


def data_preprocessing(total_text, user_id):
    vectorstore = []
    for i in range(0, len(total_text)):
        res = {}
        a = total_text[i]
        ascii_vector_id = a
        res["id"] = ascii_vector_id
        res["values"] = get_embeddings(total_text[i]).tolist()
        vectorstore.append(res)
    return store_to_pinecone(vectorstore, user_id)


def store_to_pinecone(vectorstore, user_id):
    index.upsert(vectors=vectorstore, namespace=user_id)
    return "Vector Stored"


def ask_question(user_id, queryy):
    query_embeddings = get_embeddings(queryy).tolist()
    res = index.query(vector=query_embeddings, top_k=2, namespace=user_id)
    final = ""
    for i in res["matches"]:
        final += i["id"]
    return final

