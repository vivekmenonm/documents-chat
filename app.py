import streamlit as st
import os
import tempfile
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import (
    CSVLoader,
    PyMuPDFLoader,
    UnstructuredWordDocumentLoader
)
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
db_url = os.getenv("DATABASE_URL")

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    queries = relationship("Query", back_populates="user")

class Query(Base):
    __tablename__ = 'queries'
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="queries")

Base.metadata.create_all(bind=engine)

def register_user(username, password):
    db = SessionLocal()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(username=username, password=hashed_pw)
    db.add(user)
    db.commit()

def authenticate(username, password):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user and bcrypt.checkpw(password.encode(), user.password.encode()):
        return user
    return None

# Streamlit setup
st.set_page_config(page_title="LangChain Chat App", layout="centered")
st.title("\U0001F4C4 Chat with Your Documents")

# Auth UI
st.sidebar.header("\U0001F512 User Authentication")

if "user" not in st.session_state:
    choice = st.sidebar.radio("Choose", ["Login", "Register"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if choice == "Login":
        if st.sidebar.button("Login"):
            user = authenticate(username, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")
    else:
        if st.sidebar.button("Register"):
            try:
                register_user(username, password)
                st.sidebar.success("Registration successful. Please login.")
            except Exception:
                st.sidebar.error("Username might already exist.")
else:
    st.sidebar.success(f"Logged in as {st.session_state.user.username}")
    if st.sidebar.button("Logout"):
        del st.session_state.user
        st.rerun()

if "user" in st.session_state:
    if "qa" not in st.session_state:
        st.session_state.qa = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files_info" not in st.session_state:
        st.session_state.uploaded_files_info = []

    tab1, tab2, tab3, tab4 = st.tabs(["\U0001F682 Train", "\U0001F4AC Chat", "\U0001F5C3 Chat History", "\U0001F4C2 Trained Docs"])

    with tab1:
        st.subheader("\U0001F4C4 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDFs, CSVs, DOCX or Excel files", 
            type=["pdf", "csv", "docx", "xlsx"],
            accept_multiple_files=True
        )

        if uploaded_files:
            docs = []
            filenames = []
            for uploaded_file in uploaded_files:
                ext = uploaded_file.name.split(".")[-1].lower()
                filenames.append(uploaded_file.name)

                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                if ext == "pdf":
                    loader = PyMuPDFLoader(tmp_path)
                    docs.extend(loader.load())
                elif ext == "csv":
                    loader = CSVLoader(file_path=tmp_path)
                    docs.extend(loader.load())
                elif ext == "docx":
                    loader = UnstructuredWordDocumentLoader(tmp_path)
                    docs.extend(loader.load())
                elif ext == "xlsx":
                    try:
                        df = pd.read_excel(tmp_path)
                        content = df.to_string(index=False)
                        docs.append(Document(page_content=content, metadata={"source": uploaded_file.name}))
                    except Exception as e:
                        st.error(f"Error reading Excel: {e}")

            if st.button("\U0001F682 Train"):
                try:
                    st.info("Training ....")
                    embeddings = OpenAIEmbeddings()
                    vectorstore = FAISS.from_documents(docs, embeddings)
                    retriever = vectorstore.as_retriever()
                    st.session_state.qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(), retriever=retriever)
                    st.session_state.uploaded_files_info = filenames
                    st.success("\u2705 Training complete! You can now switch to the Chat tab.")
                except Exception as e:
                    st.error(f"Embedding error: {e}")
        else:
            st.info("Upload files to begin training.")

    with tab2:
        st.subheader("\U0001F4AC Chat with Documents")

        if st.session_state.qa:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            prompt = st.chat_input("Ask something about your documents...")
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = st.session_state.qa.run(prompt)
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})

                            db = SessionLocal()
                            db.add(Query(
                                question=prompt,
                                answer=response,
                                user_id=st.session_state.user.id
                            ))
                            db.commit()
                        except Exception as e:
                            st.error(f"Failed to respond: {e}")
        else:
            st.info("Please train the documents first in the 'Train' tab.")

    with tab3:
        st.subheader("\U0001F5C3 Your Chat History")
        db = SessionLocal()
        history = db.query(Query).filter(Query.user_id == st.session_state.user.id).order_by(Query.timestamp.desc()).all()

        if history:
            for q in history:
                st.markdown(f"**Q:** {q.question}")
                st.markdown(f"**A:** {q.answer}")
                st.caption(f"\U0001F552 {q.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.info("No chat history found.")

    with tab4:
        st.subheader("\U0001F4C2 Last Trained Document List")

        if st.session_state.uploaded_files_info:
            for file in st.session_state.uploaded_files_info:
                st.markdown(f"- \U0001F4C4 {file}")
        else:
            st.info("No documents trained yet.")