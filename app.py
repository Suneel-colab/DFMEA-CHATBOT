# app.py
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI

# ----- Load .env -----
load_dotenv()  # reads .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.warning("OPENAI_API_KEY not found. Put your key in a .env file or set env variable.")
client = OpenAI(api_key=OPENAI_API_KEY)

# ----- Simple Streamlit UI -----
st.title("📊 Excel Chatbot with LLM")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
if uploaded_file is None:
    st.info("Upload an Excel file to start chatting with your data.")
    st.stop()

# Read Excel (first sheet)
try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Error reading Excel: {e}")
    st.stop()

st.subheader("Preview of Data")
st.dataframe(df)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions about a tabular dataset. Use the provided column names and data samples to answer precisely."}
    ]
if "chat" not in st.session_state:
    st.session_state.chat = []  # list of (user, assistant)

# User input
question = st.text_input("Ask a question about your data:")

def build_context(df):
    cols = ", ".join(df.columns.astype(str).tolist())
    sample = df.head(5).to_csv(index=False)
    context = (
        "Column names: " + cols + "\n\n"
        "Sample of first 5 rows (CSV):\n" + sample + "\n\n"
        "If needed, say you cannot answer precisely and suggest how to filter or examine the data."
    )
    return context

def query_llm(system_messages, user_prompt):
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=system_messages + [{"role": "user", "content": user_prompt}],
            max_tokens=400,
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"LLM request failed: {e}"

if question:
    user_q = question.strip()
    lower = user_q.lower()

    if "columns" in lower or "what columns" in lower:
        answer = f"Columns: {', '.join(df.columns.astype(str).tolist())}"
    elif "rows" in lower or "how many rows" in lower:
        answer = f"Number of rows: {len(df)}"
    else:
        context = build_context(df)
        short_prompt = f"{context}\n\nQuestion: {user_q}\nAnswer as concisely as possible."
        st.session_state.messages.append({"role": "user", "content": short_prompt})
        answer = query_llm(st.session_state.messages[:-1], short_prompt)

    st.session_state.chat.append(("You", user_q))
    st.session_state.chat.append(("Assistant", answer))

# Display chat
if st.session_state.chat:
    st.markdown("### 💬 Chat")
    for speaker, text in st.session_state.chat[::-1]:  # newest first
        if speaker == "You":
            st.markdown(f"**You:** {text}")
        else:
            st.markdown(f"**Assistant:** {text}")















