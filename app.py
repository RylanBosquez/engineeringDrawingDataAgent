import streamlit as st
import re
from core.vectorDB import loadDrawingCollection, queryDrawings
from core.dataAI import streamResponse

# Streamlit UI setup
st.set_page_config(page_title="Engineering Drawing Agent 🤖", layout="centered")
st.title("Engineering Drawing Agent 🤖")

# Load vector DB once
collection = loadDrawingCollection()

# Session state for chat history and memory
if "chatHistory" not in st.session_state:
    st.session_state.chatHistory = []
if "lastDrawingNumber" not in st.session_state:
    st.session_state.lastDrawingNumber = None

# Display previous chat history
for msg in st.session_state.chatHistory:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
userInput = st.chat_input("Type your message...")
if userInput:
    
    st.session_state.chatHistory.append({"role": "user", "content": userInput})
    with st.chat_message("user"):
        st.markdown(userInput)

    userInput = userInput.strip().upper()
    
    # Drawing number detection
    matchFull = re.search(r"R\d{7}", userInput)
    matchPartial = re.search(r"\b\d{7}\b", userInput)

    if matchFull:
        drawingNumber = matchFull.group(0)
        st.session_state.lastDrawingNumber = drawingNumber
        queryInput = drawingNumber
    elif matchPartial:
        drawingNumber = "R" + matchPartial.group(0)
        st.session_state.lastDrawingNumber = drawingNumber
        queryInput = drawingNumber
    elif "previous part" in userInput.lower() and st.session_state.lastDrawingNumber:
        queryInput = st.session_state.lastDrawingNumber
    else:
        queryInput = userInput

    # Query vector DB
    results = queryDrawings(collection, queryInput)
    context = "\n\n".join(results)

    # Stream AI response
    with st.chat_message("assistant"):
        responseContainer = st.empty()
        streamedText = ""
        for chunk in streamResponse(context, userInput):
            streamedText += chunk
            responseContainer.markdown(streamedText + "▌")
        responseContainer.markdown(streamedText)

    st.session_state.chatHistory.append({"role": "assistant", "content": streamedText})
