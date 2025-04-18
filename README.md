```markdown
# 📄 LangChain Chat App with Authentication

Chat with your documents! Upload PDFs, DOCX, CSV, or Excel files, embed them using OpenAI + FAISS, and interact with them using a LangChain-powered chatbot. This app is built with Streamlit and supports user authentication and chat history logging in PostgreSQL.

---

## 🧰 Features

- 🔐 User Authentication (Register/Login)
- 📤 Upload documents (PDF, DOCX, CSV, Excel)
- 🧠 Embedding via OpenAI + FAISS
- 💬 Conversational Q&A with LangChain + OpenAI
- 🕓 Per-user chat history
- 📁 View list of last trained documents

---

## 🏗️ Tech Stack

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [OpenAI API](https://platform.openai.com/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [bcrypt](https://pypi.org/project/bcrypt/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/langchain-chat-app.git
cd langchain-chat-app
```

### 2. Create Virtual Environment and Install Dependencies

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/<your_database>
```

## ✅ 1. **Install PostgreSQL**

### For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

### Start PostgreSQL service:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## ✅ 2. **Create Database, User & Grant Access**

### Step A: Enter PostgreSQL shell as the default `postgres` user:
```bash
sudo -u postgres psql
```

### Step B: Run these commands inside the psql shell:
```sql
-- Create user
CREATE USER <username> WITH PASSWORD <NewStrongPassword123!>;

-- Create database
CREATE DATABASE <your_database> OWNER <user_name>;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE microsaas_db TO microsaas;
```

### Step C: Exit psql
```sql
\q
```

---

## ✅ 3. **Update `.env` or Code**

In your `.env` file:
```env
DATABASE_URL=postgresql://<username>:<NewStrongPassword123!>@localhost:5432/<your_database>
```

---

## ✅ 4. **(Optional) Enable Remote Access**
If your app is outside the VM or container:

### Edit `postgresql.conf`:
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Find:
```
#listen_addresses = 'localhost'
```
Change to:
```
listen_addresses = '*'
```

### Edit `pg_hba.conf`:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add at the end:
```
host    all             all             0.0.0.0/0               md5
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---
## ✅ 5. **Test Connection**
Try using a Postgres client or:
```bash
psql -h localhost -U <username> -d <your_database>
```
### 5. Run the App

```bash
streamlit run app.py
```

---

## 🗃️ Folder Structure

```
langchain-chat-app/
│
├── app.py                  # Main Streamlit app
├── .env                    # API keys and DB credentials
├── requirements.txt        # Python dependencies
└── README.md               # Project overview
```

---

## 🧪 App Workflow

1. **Register or Login** using the sidebar.
2. Upload one or more files under the **Train** tab.
3. Click **Train** to embed documents using OpenAI + FAISS.
4. Ask questions under the **Chat** tab.
5. Check past Q&As under the **Chat History** tab.
6. View uploaded files under **Trained Docs** tab.

---

## 📊 Database Schema

- `users`: Stores usernames and hashed passwords.
- `queries`: Stores questions, answers, timestamps, and user IDs.

---

## 💡 Example Prompt

> _"Summarize the uploaded document."_  
> _"What are the key points in the Excel sheet?"_

---

## ❗ Notes

- FAISS vectors are stored in memory and lost on restart. Persistent vectorstore setup is recommended for production.
- Ensure all uploaded document types are properly formatted and supported.

---

## 📬 Contact

For issues, suggestions, or contributions, open a GitHub issue or email: `vivekmadathiveetil@gmail.com`

---

## 📝 License

MIT License © 2025 Vivek Menon M
