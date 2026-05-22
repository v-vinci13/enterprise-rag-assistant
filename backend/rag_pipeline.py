import chromadb
import requests
from sentence_transformers import SentenceTransformer
from auth import check_access

# =========================
# Embedding Model
# =========================

model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# ChromaDB
# =========================

client = chromadb.PersistentClient(path="../chroma_db")

try:
    collection = client.get_collection("enterprise_docs")
except:
    collection = client.get_or_create_collection("enterprise_docs")


# =========================
# INTENT DETECTION AGENT
# =========================

def detect_intent(query):

    query = query.lower()

    if "leave" in query or "policy" in query:
        return "HR"

    elif "finance" in query or "revenue" in query:
        return "Finance"

    elif "security" in query or "login" in query:
        return "Security"

    return "General"


# =========================
# RETRIEVAL + RBAC
# =========================

def retrieve(query, username):

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    docs = []
    scores = []

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        source = meta.get("source", "unknown")

        # RBAC CHECK
        if check_access(username, source):

            # convert distance → similarity score
            similarity = 1 / (1 + dist)

            docs.append((doc, source))
            scores.append(similarity)

    return docs, scores


# =========================
# MAIN PIPELINE
# =========================

def generate_answer(query, username):

    intent = detect_intent(query)

    docs, scores = retrieve(query, username)

    if not docs:
        return f"""
Intent: {intent}

❌ Access denied or no relevant documents found.

Confidence Score: 0%
Sources: None
"""

    context = ""
    citations = []

    for doc, source in docs:
        context += doc + "\n\n"
        citations.append(source)

    # =========================
    # CONFIDENCE SCORE (IMPROVED)
    # =========================

    
    if len(scores) == 0:
        confidence = 0.0
    else:
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        # strong match boost
        if max_score > 0.80:
            boost = 1.25
        elif max_score > 0.65:
            boost = 1.1
        else:
            boost = 1.0

        confidence = (max_score * 0.7 + avg_score * 0.3) * 100 * boost

    confidence = min(round(confidence, 2), 100)
        # =========================
    # PROMPT
    # =========================

    prompt = f"""
You are a STRICT enterprise RAG assistant.

RULES:
- Use ONLY the given context.
- DO NOT guess or infer anything.
- If information is missing, say:
  "I do not have enough information in the provided context."
- DO NOT use phrases like "seems", "likely", "probably".
- Be factual and exact.


CONTEXT:
{context}

QUESTION:
{query}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    final_answer = response.json()["response"]

    for word in ["therefore", "implies", "as a result", "so"]:
        final_answer = final_answer.replace(word, "")
    bad_phrases = ["seems", "likely", "probably", "appears"]

    for phrase in bad_phrases:
        final_answer = final_answer.replace(phrase, "")

    # =========================
    # CLEAN TEXT OUTPUT (NO JSON)
    # =========================

    return f"""

 Intent: {intent}

 Answer:
{final_answer}

 Confidence Score: {confidence}%

Sources:
{', '.join(set(citations))}

"""