import os
import torch
from dotenv import load_dotenv
from pinecone import Pinecone, PodSpec
from transformers import AutoTokenizer, AutoModel
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")
pinecone_api_key=os.getenv("PINECONE_API_KEY")

index_name="rag"
loader = PyPDFLoader("1.pdf")
pages = loader.load_and_split()
pc = Pinecone(api_key=pinecone_api_key)
pc.delete_index(index_name)
index=pc.create_index(
    name="rag",
    dimension=384, 
    metric="cosine",
    spec=PodSpec(
    environment="gcp-starter",
    pod_type="s1.x1",
    pods=1
  )
    )
index = pc.Index(index_name)

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 20)
total_text=[]


for page in pages:
    texts = text_splitter.split_text(page.page_content)
    docs=[]
    for text in texts:
        docs.append(text)
    total_text+=docs


model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embeddings(text):
    input_ids = tokenizer(text, return_tensors="pt")["input_ids"]
    with torch.no_grad():
        embeddings = model(input_ids)["last_hidden_state"].mean(dim=1)
        return embeddings.numpy()[0]

vectorstore=[]

for i in range(0, len(total_text)):
    res={}
    a=total_text[i]
    ascii_vector_id = a.encode('ascii', 'ignore').decode('ascii')
    res["id"]=ascii_vector_id
    res["values"]=get_embeddings(total_text[i]).tolist()
    vectorstore.append(res)
    res={}



def store_to_pinecone(vectorstore):
    index.upsert(
    vectors=vectorstore
)
store_to_pinecone(vectorstore)

