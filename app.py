import streamlit as st
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")
API_URL = os.getenv("API_URL")

st.title("ActuLLM")
st.caption("Ok Kévin, il se passe quoi dans le monde ?")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.header("Administration")

    # Model selector
    model_choice = st.radio("Modèle LLM", ["Mistral (Ollama)", "GPT (Azure)"], index=0)
    provider = "ollama" if model_choice == "Mistral (Ollama)" else "azure"

    st.divider()

    # News count
    try:
        health = requests.get(f"{API_URL}/health").json()
        st.metric("Articles indexés", health.get("news count", 0))
        st.caption(f"Modèle actif : {health.get('model', '?')}")
    except Exception:
        st.warning("API non disponible")

    st.divider()

    # Ingest button
    if st.button("Mettre à jour les articles", use_container_width=True):
        with st.spinner("Ingestion en cours..."):
            try:
                res = requests.post(f"{API_URL}/ingest")
                if res.ok:
                    st.success("Articles mis à jour !")
                    st.rerun()
                else:
                    st.error(f"Erreur : {res.json().get('detail', 'Inconnue')}")
            except Exception as e:
                st.error(f"Erreur : {e}")

# ─────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Posez votre question sur l'actualité..."):

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Avec RAG")
        with st.spinner("Recherche en cours..."):
            try:
                response_rag = requests.post(
                    f"{API_URL}/ask/rag",
                    json={"question": user_input, "provider": provider}
                )
                answer_rag = response_rag.json()["answer"]
            except Exception as e:
                answer_rag = f"Erreur : {e}"
            st.markdown(answer_rag)

    with col2:
        st.subheader("❌ Sans RAG")
        with st.spinner("Génération en cours..."):
            try:
                response_plain = requests.post(
                    f"{API_URL}/ask/plain",
                    json={"question": user_input, "provider": provider}
                )
                answer_plain = response_plain.json()["answer"]
            except Exception as e:
                answer_plain = f"Erreur : {e}"
            st.markdown(answer_plain)

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"**Avec RAG:** {answer_rag}\n\n**Sans RAG:** {answer_plain}"
    })