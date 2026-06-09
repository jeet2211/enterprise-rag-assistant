SYSTEM_PROMPT = (
    "You are an enterprise assistant that answers only from the supplied context. "
    "If the answer is not in the context, say that you could not find it in the uploaded documents. "
    "Always be concise and cite the document name and page number when relevant."
)


def build_prompt(history: str, context: str, question: str) -> str:
    return f"""SYSTEM:
{SYSTEM_PROMPT}

HISTORY:
{history or "No prior conversation."}

CONTEXT:
{context or "No relevant document context found."}

QUESTION:
{question}

Answer with grounded facts only. If you cite a source, use the document name and page number.
"""

