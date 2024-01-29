from transformers import AutoTokenizer, AutoModel
import torch
from dotenv import load_dotenv
load_dotenv()
import os
from pinecone import Pinecone
pinecone_api_key=os.getenv("PINECONE_API_KEY")

index_name="rag"
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(index_name)

model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embeddings(text):
    input_ids = tokenizer(text, return_tensors="pt")["input_ids"]
    with torch.no_grad():
        embeddings = model(input_ids)["last_hidden_state"].mean(dim=1)
        return embeddings.numpy()[0]

def store_to_pinecone(vectorstore):
    index.upsert(
    vectors=vectorstore
)
    
query="Explain the internal mechanism of k hop clustering in detail"
query_embeddings=get_embeddings(query).tolist()
res=index.query(vector=query_embeddings, top_k=3)
final=""
for i in res["matches"]:
    final+=i["id"]

print(final)