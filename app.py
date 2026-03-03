
import streamlit as st

st.title(" ActuLLM")
st.caption("Ok Kévin, il se passe quoi dans le monde ?")

# toggle RAG on/off
use_rag = st.sidebar.toggle("Activer le RAG", value=True)

# keep message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# B1 - get user input
if user_input := st.chat_input("Posez votre question sur l'actualité..."):

    # save and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)


    # B2 - call the API
    with st.chat_message("assistant"):
        with st.spinner("Kévin réfléchit..."):

            endpoint = "/ask/rag" if use_rag else "/ask/plain"
            response = requests.post(
                f"{API_URL}{endpoint}",
                json={"question": user_input}
            )
            answer = response.json()["answer"]
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})


