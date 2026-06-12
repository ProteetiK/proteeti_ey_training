!pip install langchain langchain-community langchain-groq faiss-cpu

import os
from getpass import getpass
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
GROQ_API_KEY = ""
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
faqs = [
    "How do I reset my password? Click Forgot Password on login.",
    "How do I change my subscription? Go to Billing > Plans.",
    "How do I cancel my subscription? Billing > Cancel Subscription.",
    "What payment methods are supported? Visa Mastercard PayPal.",
    "How do I update billing details? Billing > Payment Methods.",
    "Can I export my data? Settings > Export Data.",
    "How do I invite team members? Team > Invite Users.",
    "Does the product support 2FA? Enable it in Security Settings.",
    "How do I contact support? Email support@example.com.",
    "Where can I download invoices? Billing > Invoices."
]
docs = [Document(page_content=f) for f in faqs]
db = FAISS.from_documents(docs, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)
print("FAQ Bot (type 'exit' to quit)")
while True:
    query = input("\nYou: ").strip()
    if query.lower() == "exit":
        break
    hits = db.similarity_search_with_score(query, k=2)
    context = "\n".join(
        doc.page_content for doc, _ in hits
    )
    answer = llm.invoke(
        f"""Answer ONLY from the FAQ context.
FAQ:
{context}
Question: {query}
If the answer is unavailable, say:
'I couldn't find that in the FAQ.'
"""
    ).content
    print("\nBot:", answer)
    print("Top Matches:")
    for doc, score in hits:
        print(f"score={score:.4f} | {doc.page_content}")
