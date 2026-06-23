import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_DIM = 384

embedder = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

index = faiss.IndexFlatL2(
    EMBED_DIM
)

documents = []


def remember(
    text: str,
    metadata=None
):

    metadata = metadata or {}

    embedding = embedder.encode(
        [text]
    )

    index.add(
        np.array(
            embedding,
            dtype="float32"
        )
    )

    documents.append(
        {
            "text": text,
            "metadata": metadata
        }
    )


def recall(
    query: str,
    k: int = 3
):

    if len(documents) == 0:
        return []

    embedding = embedder.encode(
        [query]
    )

    _, indices = index.search(
        np.array(
            embedding,
            dtype="float32"
        ),
        min(k, len(documents))
    )

    results = []

    for idx in indices[0]:

        if idx < len(documents):
            results.append(
                documents[idx]
            )

    return results


def memory_context(
    query: str,
    k: int = 3
):

    hits = recall(
        query,
        k=k
    )

    if not hits:
        return ""

    lines = []

    for hit in hits:
        lines.append(
            hit["text"]
        )

    return "\n".join(lines)