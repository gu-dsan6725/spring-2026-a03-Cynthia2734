import logging

logger = logging.getLogger(__name__)

_DEPENDENCY_KW = {
    "depend",
    "package",
    "requirement",
    "library",
    "install",
    "pyproject",
    "package.json",
    "pip",
    "npm",
}

_STRUCTURE_KW = {
    "entry point",
    "main file",
    "structure",
    "language",
    "file type",
    "directory",
    "folder",
    "layout",
    "programming language",
    "what files",
}

_API_KW = {
    "endpoint",
    "api",
    "route",
    "rest",
    "http",
    "request",
    "response",
    "scope",
}

_AUTH_KW = {
    "auth",
    "token",
    "oauth",
    "jwt",
    "login",
    "authorization",
    "credential",
    "keycloak",
    "cognito",
    "permission",
    "validate",
}

_DOCS_KW = {
    "how",
    "add",
    "implement",
    "support",
    "modify",
    "interface",
    "architecture",
    "would you",
    "what files would",
}


def classify_query(question: str) -> str:
    """
    Classify a user question to determine which bash retrieval strategy to use.

    Args:
        question: The user's natural language question about the codebase.

    Returns:
        One of: 'dependency', 'structure', 'auth', 'api', 'docs', 'code_search'
    """
    q = question.lower()

    if any(kw in q for kw in _DEPENDENCY_KW):
        query_type = "dependency"
    elif any(kw in q for kw in _STRUCTURE_KW):
        query_type = "structure"
    elif any(kw in q for kw in _API_KW):
        query_type = "api"
    elif any(kw in q for kw in _AUTH_KW):
        query_type = "auth"
    elif any(kw in q for kw in _DOCS_KW):
        query_type = "docs"
    else:
        query_type = "code_search"
    return query_type
