import time
import logging

from langchain_community.chat_models import ChatLiteLLM
from langchain_core.prompts import ChatPromptTemplate

from .classifier import classify_query
from .retriever import retrieve_context

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = (
    "You are an expert software engineer analyzing the mcp-gateway-registry codebase. "
    "You are given context retrieved from the codebase using bash tools (grep, find, cat, tree). "
    "Answer the user's question based ONLY on the provided context. "
    "Always cite specific file names when referencing code. "
    "If the context is insufficient to answer fully, say so clearly. "
    "Keep your answer concise but thorough.\n\n"
    "{context}"
)

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_PROMPT),
        ("human", "{input}"),
    ]
)


class Part1Pipeline:
    """
    Encapsulates the LLM and codebase path so both can be configured once
    and reused across multiple questions.

    Args:
        model_id:      LiteLLM model string, e.g. 'groq/llama-3.1-8b-instant'.
        codebase_path: Path to the root of the target codebase.
        temperature:   LLM temperature (default 0 for deterministic answers).
        max_retries:   Number of retry attempts on rate-limit errors.
    """

    def __init__(
        self,
        model_id: str = "groq/llama-3.1-8b-instant",
        codebase_path: str = "../mcp-gateway-registry",
        temperature: float = 0,
        max_retries: int = 5,
    ):
        self.model_id = model_id
        self.codebase_path = codebase_path
        self.max_retries = max_retries
        self.llm = ChatLiteLLM(model=model_id, temperature=temperature)
        logger.info(f"Part1Pipeline initialised (model={model_id})")

    def answer(self, question: str) -> dict:
        """
        Full pipeline: classify → retrieve context via bash → generate answer.

        Args:
            question: The user's question about the codebase.

        Returns:
            dict with keys: 'question', 'query_type', 'context', 'answer'
        """
        logger.info(f"Question: {question}")
        
        query_type = classify_query(question)
        context = retrieve_context(question, query_type, self.codebase_path)
        messages = _PROMPT.format_messages(context=context, input=question)

        for attempt in range(self.max_retries):
            try:
                response = self.llm.invoke(messages)
                answer = response.content
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

        raise RuntimeError(f"answer_question failed after {self.max_retries} retries")


def build_pipeline(
    model_id: str = "groq/llama-3.1-8b-instant",
    codebase_path: str = "../mcp-gateway-registry",
) -> Part1Pipeline:
    """Return a ready-to-use Part1Pipeline instance."""
    return Part1Pipeline(model_id=model_id, codebase_path=codebase_path)


def answer_question(question: str, pipeline: Part1Pipeline | None = None) -> dict:
    """
    Module-level convenience wrapper so the notebook can call:
        from src.part1 import answer_question
        result = answer_question("What deps are used?")

    A default pipeline (groq/llama-3.1-8b-instant, '../mcp-gateway-registry')
    is created on first call and reused.
    """
    global _default_pipeline
    if pipeline is not None:
        return pipeline.answer(question)
    if "_default_pipeline" not in globals() or _default_pipeline is None:
        _default_pipeline = build_pipeline()
    return _default_pipeline.answer(question)
