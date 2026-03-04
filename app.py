# app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")
API_URL = os.getenv("API_URL")

st.title(" ActuLLM")
st.caption("Ok Kévin, il se passe quoi dans le monde ?")

# initialize history FIRST before anything else
if "messages" not in st.session_state:
    st.session_state.messages = []

# display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# single chat input
if user_input := st.chat_input("Posez votre question sur l'actualité..."):

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # two columns side by side
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Avec RAG")
        with st.spinner("Recherche en cours..."):
            response_rag = requests.post(
                f"{API_URL}/ask/rag",
                json={"question": user_input}
            )
            answer_rag = response_rag.json()["answer"]
            st.markdown(answer_rag)

    with col2:
        st.subheader("❌ Sans RAG")
        with st.spinner("Génération en cours..."):
            response_plain = requests.post(
                f"{API_URL}/ask/plain",
                json={"question": user_input}
            )
            answer_plain = response_plain.json()["answer"]
            st.markdown(answer_plain)

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"**Avec RAG:** {answer_rag}\n\n**Sans RAG:** {answer_plain}"
    })