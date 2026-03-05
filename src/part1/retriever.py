import logging
from .bash_tool import run_bash

logger = logging.getLogger(__name__)


def retrieve_context(
    question: str, query_type: str, codebase_path: str = "../mcp-gateway-registry"
) -> str:
    """
    Select and execute bash commands appropriate for the query type.
    Context is kept under 4 000 chars to avoid Groq TPM rate limits.

    Args:
        question:      The original user question.
        query_type:    Category returned by classify_query().
        codebase_path: Path to the root of the target codebase.

    Returns:
        Retrieved context as a single string to pass to the LLM.
    """

    def bash(cmd: str, max_chars: int = 8000) -> str:
        return run_bash(cmd, cwd=codebase_path, max_chars=max_chars)

    parts = []

    if query_type == "dependency":
        parts.append("=== pyproject.toml - dependencies ===")
        parts.append(
            bash("grep -A 60 '\\[project\\]' pyproject.toml | head -70", max_chars=2500)
        )

        parts.append("\n=== auth_server/pyproject.toml - dependencies ===")
        parts.append(
            bash(
                "grep -A 30 'dependencies' auth_server/pyproject.toml | head -35",
                max_chars=1000,
            )
        )

        parts.append("\n=== cli/package.json (name + dependencies only) ===")
        parts.append(
            bash(
                "python3 -c \"import json; d=json.load(open('cli/package.json')); "
                "print('name:', d.get('name')); "
                "[print(k+': '+v) for k,v in d.get('dependencies',{}).items()]\"",
                max_chars=800,
            )
        )

    elif query_type == "structure":
        parts.append("=== Directory Structure (depth 2) ===")
        parts.append(bash("tree -L 2 --dirsfirst", max_chars=1500))

        parts.append("\n=== File Types Count ===")
        parts.append(
            bash(
                "find . -not -path './.git/*' -type f | "
                "sed 's/.*\\.//' | sort | uniq -c | sort -rn | head -15"
            )
        )

        parts.append("\n=== registry/main.py (first 40 lines) ===")
        parts.append(bash("head -40 registry/main.py"))

        parts.append("\n=== Entry point from Dockerfile ===")
        parts.append(bash("grep -E 'CMD|ENTRYPOINT|python|uvicorn' Dockerfile"))

    elif query_type == "auth":
        parts.append("=== auth_server/server.py (first 80 lines) ===")
        parts.append(bash("head -80 auth_server/server.py", max_chars=2000))

        parts.append("\n=== OAuth providers config ===")
        parts.append(bash("cat auth_server/oauth2_providers.yml", max_chars=1000))

        parts.append("\n=== Auth function definitions ===")
        parts.append(
            bash(
                r"grep -rn 'def.*token\|def.*auth\|def.*scope\|def.*validate' "
                "--include='*.py' registry/auth/ | head -30"
            )
        )

        parts.append("\n=== docs/auth.md (first 60 lines) ===")
        parts.append(bash("head -60 docs/auth.md", max_chars=1500))

    elif query_type == "api":
        parts.append("=== API route decorators ===")
        parts.append(
            bash(r"grep -rn '@router\.' --include='*.py' registry/api/ | head -40")
        )

        parts.append("\n=== Scope requirements ===")
        parts.append(
            bash(
                r"grep -rn 'require_scope\|security' "
                "--include='*.py' registry/api/ | head -30"
            )
        )

        parts.append("\n=== auth_server/scopes.yml ===")
        parts.append(bash("cat auth_server/scopes.yml", max_chars=1500))

        parts.append("\n=== registry/api/ files ===")
        parts.append(bash("find registry/api -name '*.py' | sort"))

    elif query_type == "docs":
        parts.append("=== auth_server/providers/ files ===")
        parts.append(bash("ls auth_server/providers/"))

        parts.append("\n=== Example provider implementation (first 60 lines) ===")
        parts.append(
            bash("head -60 $(ls auth_server/providers/*.py | head -1)", max_chars=1500)
        )

        parts.append("\n=== oauth2_providers.yml ===")
        parts.append(bash("cat auth_server/oauth2_providers.yml", max_chars=1000))

        parts.append("\n=== docs/auth.md (first 50 lines) ===")
        parts.append(bash("head -50 docs/auth.md", max_chars=1000))

        parts.append("\n=== docs/registry-auth-architecture.md (first 50 lines) ===")
        parts.append(
            bash("head -50 docs/registry-auth-architecture.md", max_chars=1000)
        )

    else:
        parts.append("=== registry/ structure ===")
        parts.append(bash("tree -L 2 --dirsfirst registry/", max_chars=1000))
        parts.append(bash(f"grep -rn '{question[:30]}' --include='*.py' -l | head -10"))

    context = "\n".join(parts)
    logger.info(f"retrieve_context [{query_type}]: {len(context)} chars")
    return context
