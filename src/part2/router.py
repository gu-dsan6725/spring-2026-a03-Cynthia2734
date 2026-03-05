import logging

logger = logging.getLogger(__name__)


_CSV_KW = [
    "revenue",
    "sales",
    "units sold",
    "total",
    "highest",
    "lowest",
    "region",
    "volume",
    "how many",
    "how much",
    "average",
    "sum",
    "december",
    "october",
    "november",
    "month",
    "quarter",
    "selling",
    "sold",
    "price",
    "trend",
]

_TEXT_KW = [
    "feature",
    "review",
    "customer",
    "description",
    "spec",
    "what do",
    "ease",
    "cleaning",
    "quality",
    "rated",
    "rating",
    "headphone",
    "air fryer",
    "product page",
    "say about",
    "opinion",
    "feedback",
    "recommend",
    "pros",
    "cons",
]


def classify_query(question: str) -> str:
    """
    Route a question to the appropriate data source(s).

    Args:
        question: The user's natural language question.

    Returns:
        One of: 'csv', 'text', 'both'
    """
    q = question.lower()

    has_csv: bool = any(kw in q for kw in _CSV_KW)
    has_text: bool = any(kw in q for kw in _TEXT_KW)

    if has_csv and has_text:
        query_type = "both"
    elif has_csv:
        query_type = "csv"
    elif has_text:
        query_type = "text"
    else:
        query_type = "both"

    preview: str = question[:60]
    logger.info(f"classify_query: [{query_type}] {preview}")
    return query_type
