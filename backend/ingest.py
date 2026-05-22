import chromadb
import fitz
import pandas as pd
import json

from sentence_transformers import SentenceTransformer

# =========================
# Embedding Model
# =========================

model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# ChromaDB
# =========================

client = chromadb.PersistentClient(path="../chroma_db")

# IMPORTANT
collection = client.get_or_create_collection(
    name="enterprise_docs"
)

# =========================
# PDF INGESTION
# =========================

pdf_path = "../dataset/pdfs/hr_policy.pdf"

doc = fitz.open(pdf_path)

pdf_text = ""

for page in doc:
    pdf_text += page.get_text()

embedding = model.encode(pdf_text).tolist()

collection.add(
    documents=[pdf_text],
    embeddings=[embedding],
    metadatas=[{"source": "hr_policy.pdf"}],
    ids=["pdf1"]
)

# =========================
# CSV INGESTION
# =========================

csv_path = "../dataset/csv/finance_q1.csv"

df = pd.read_csv(csv_path)

csv_text = df.to_string()

embedding = model.encode(csv_text).tolist()

collection.add(
    documents=[csv_text],
    embeddings=[embedding],
    metadatas=[{"source": "finance_q1.csv"}],
    ids=["csv1"]
)

# =========================
# JSON LOG INGESTION
# =========================

json_path = "../dataset/logs/security_logs.json"

with open(json_path) as f:
    logs = json.load(f)

log_text = json.dumps(logs)

embedding = model.encode(log_text).tolist()

collection.add(
    documents=[log_text],
    embeddings=[embedding],
    metadatas=[{"source": "security_logs.json"}],
    ids=["json1"]
)

print("Data ingestion completed.")