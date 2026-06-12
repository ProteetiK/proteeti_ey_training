!pip -q install groq sentence-transformers scikit-learn pandas

import os
import pandas as pd
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

os.environ["GROQ_API_KEY"] = ""
client = Groq(api_key=os.environ["GROQ_API_KEY"])

embedder = SentenceTransformer("all-MiniLM-L6-v2")

data = [
    {
        "question": "What is the capital of France?",
        "context": """
        France is a country in Western Europe.
        Paris is the capital and largest city of France.
        The Eiffel Tower is located in Paris.
        """,
        "answer": "The capital of France is Paris."
    },
    {
        "question": "What is the capital of France?",
        "context": """
        France is in Europe.
        Paris is the capital city of France.
        """,
        "answer": "Paris is the capital of France and was founded by NASA."
    },
    {
        "question": "What is the capital of France?",
        "context": """
        Cricket is popular in India.
        IPL is a major cricket league.
        """,
        "answer": "The capital of France is Paris."
    }
]

def embed(text):
    return embedder.encode([text])

def cosine(a, b):
    return float(cosine_similarity(a, b)[0][0])

def groundedness_llm(question, context, answer):
    prompt = f"""
You are evaluating a RAG system.

Return JSON ONLY:
{{
  "score": 0-1,
  "reason": "short explanation"
}}

QUESTION:
{question}

CONTEXT:
{context}

ANSWER:
{answer}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

results = []

for i, item in enumerate(data, 1):

    q, c, a = item["question"], item["context"], item["answer"]

    q_emb = embed(q)
    c_emb = embed(c)
    a_emb = embed(a)

    context_relevance = cosine(q_emb, c_emb)
    answer_relevance = cosine(q_emb, a_emb)
    groundedness = groundedness_llm(q, c, a)

    results.append({
        "Scenario": i,
        "Question": q,
        "Context": c.strip(),
        "Answer": a,
        "Context_Relevance": context_relevance,
        "Answer_Relevance": answer_relevance,
        "Groundedness_Raw": groundedness
    })

import pandas as pd
import json
import re

df = pd.DataFrame(results)

def extract_score(text):
    try:
        match = re.search(r'"score"\s*:\s*([0-9.]+)', text)
        return float(match.group(1)) if match else None
    except:
        return None

def extract_reason(text):
    try:
        match = re.search(r'"reason"\s*:\s*"(.*?)"', text)
        return match.group(1) if match else text
    except:
        return text

df["Groundedness_Score"] = df["Groundedness_Raw"].apply(extract_score)
df["Groundedness_Reason"] = df["Groundedness_Raw"].apply(extract_reason)

final_df = df[[
    "Scenario",
    "Context_Relevance",
    "Answer_Relevance",
    "Groundedness_Score",
    "Groundedness_Reason"
]]

display(final_df)

print("\nSUMMARY")
print()
print("Avg Context Relevance :", final_df["Context_Relevance"].mean())
print("Avg Answer Relevance  :", final_df["Answer_Relevance"].mean())
print("Avg Groundedness      :", final_df["Groundedness_Score"].mean())

