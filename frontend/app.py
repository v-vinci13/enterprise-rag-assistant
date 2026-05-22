import streamlit as st
import requests

st.set_page_config(
    page_title="Secure Enterprise RAG Assistant"
)

st.title("Secure Enterprise RAG Assistant")

username = st.selectbox(
    "Select User",
    ["alice", "bob", "eve"]
)

# =========================
# Conversation Memory
# =========================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("Ask your question")

if st.button("Submit"):

    if query:

        # Context Awareness
        conversation_context = ""

        for item in st.session_state.chat_history[-3:]:
            conversation_context += item + "\n"

        final_query = conversation_context + query

        response = requests.post(
            "http://127.0.0.1:8000/query",
            json={
                "username": username,
                "query": final_query
            }
        )

        result = response.json()

        st.session_state.chat_history.append(query)

        st.write(result["answer"])

# =========================
# Show History
# =========================

st.subheader("Conversation History")

for item in st.session_state.chat_history:
    st.write("•", item)