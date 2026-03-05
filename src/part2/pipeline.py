import time
import logging

from langchain_community.chat_models import ChatLiteLLM
from langchain_core.prompts import ChatPromptTemplate

from .router import classify_query
from .retriever import retrieve_from_csv, retrieve_from_text

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a helpful data analyst with access to e-commerce sales data and product information. "
    "You are given context retrieved from two possible sources:\n"
    "1. Structured sales CSV data (revenue, units sold, categories, regions, dates)\n"
    "2. Unstructured product pages (descriptions, specifications, customer reviews)\n\n"
    "Answer the user's question based ONLY on the provided context. "
    "Cite specific numbers, product names, or reviews from the context when relevant. "
    "If the context doesn't contain enough information to answer fully, say so clearly. "
    "If a specific product's sales data is not present in the CSV context, "
    "state that explicitly. Do NOT estimate or infer sales figures."
    "Keep your answer concise and well-structured.\n\n"
    "{context}"
)

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", "{input}"),
    ]
)


class Part2Pipeline:
    """
    Encapsulates model config and data paths so they can be set once
    and reused across multiple questions.

    Args:
        model_id:   LiteLLM model string, e.g. 'groq/llama-3.1-8b-instant'.
        csv_path:   Path to daily_sales.csv.
        text_dir:   Directory containing *_product_page.txt files.
        max_retries: Retry attempts on rate-limit errors.
    """

    def __init__(
        self,
        model_id: str = "groq/llama-3.1-8b-instant",
        csv_path: str = "../data/structured/daily_sales.csv",
        text_dir: str = "../data/unstructured",
        max_retries: int = 5,
    ):
        self.model_id = model_id
        self.csv_path = csv_path
        self.text_dir = text_dir
        self.max_retries = max_retries
        self.llm = ChatLiteLLM(model=model_id, temperature=0)
        logger.info(f"Part2Pipeline initialised (model={model_id})")

    def retrieve_context(self, question: str, query_type: str) -> str:
        """Route retrieval to CSV, text files, or both."""
        if query_type == "csv":
            return retrieve_from_csv(question, csv_path=self.csv_path)

        elif query_type == "text":
            return retrieve_from_text(question, text_dir=self.text_dir)

        else:  # both
            csv_ctx: str = retrieve_from_csv(question, csv_path=self.csv_path)
            text_ctx: str = retrieve_from_text(
                question, text_dir=self.text_dir, max_chars=3000
            )
            combined: str = (
                "## STRUCTURED DATA (Sales CSV)\n"
                + csv_ctx
                + "\n\n## UNSTRUCTURED DATA (Product Pages)\n"
                + text_ctx
            )
            logger.info(f"Combined context length: {len(combined)} chars")
            return combined

    def answer(self, question: str) -> dict:
        """
        Full pipeline: classify → retrieve → generate answer.

        Args:
            question: The user's natural language question.

        Returns:
            dict with keys: 'question', 'query_type', 'context', 'answer'
        """
        logger.info(f"Question: {question}")

        query_type: str = classify_query(question)
        context: str = self.retrieve_context(question, query_type)
        messages = _PROMPT.format_messages(context=context, input=question)

        for attempt in range(self.max_retries):
            try:
                response = self.llm.invoke(messages)
                answer: str = response.content
                logger.info(f"Answer preview: {answer[:300]}")
                return {
                    "question": question,
                    "query_type": query_type,
                    "context": context,
                    "answer": answer,
                }
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    wait = 30 * (attempt + 1)
                    logger.warning(
                        f"Rate limit hit, waiting {wait}s… (attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(wait)
                else:
                    raise

        raise RuntimeError(f"answer failed after {self.max_retries} retries")


def build_pipeline(
    model_id: str = "groq/llama-3.1-8b-instant",
    csv_path: str = "../data/structured/daily_sales.csv",
    text_dir: str = "../data/unstructured",
) -> Part2Pipeline:
    """Return a ready-to-use Part2Pipeline."""
    return Part2Pipeline(model_id=model_id, csv_path=csv_path, text_dir=text_dir)


def answer_question(question: str, pipeline: Part2Pipeline | None = None) -> dict:
    """
    Module-level convenience wrapper.
    A default pipeline is created on first call and reused.
    """
    global _default_pipeline
    if pipeline is not None:
        return pipeline.answer(question)
    if "_default_pipeline" not in globals() or _default_pipeline is None:
        _default_pipeline = build_pipeline()
    return _default_pipeline.answer(question)
