
from __future__ import annotations

from pathlib import Path
from mcp.server.transport_security import TransportSecuritySettings
from mcp.server import MCPServer

# python -m uvicorn mcp_server.server:app --host 127.0.0.1 --port 8000   
# ngrok http 8000

transport_security = TransportSecuritySettings(
    allowed_hosts=[
        "127.0.0.1",

        "127.0.0.1:*",

        "localhost",
        "localhost:*",

        "pork-twentieth-entire.ngrok-free.dev",

        "pork-twentieth-entire.ngrok-free.dev:*",
    ],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


mcp = MCPServer(
    "mcp_fa",
)


@mcp.tool()
def get_project_tree() -> list[str]:
    """
    Επιστρέφει τα αρχεία του project ως relative paths.

    Δεν επιστρέφει directories όπως:
    - venv
    - __pycache__
    - .git

    ώστε να μην γεμίζουμε τον client με άχρηστα αρχεία.
    """

    ignored_directories = {
        "venv",
        "__pycache__",
        ".git",
        ".ipynb_checkpoints",
    }

    project_files: list[str] = []

    for path in PROJECT_ROOT.rglob("*"):

        if not path.is_file():
            continue

        if any(
            part in ignored_directories
            for part in path.parts
        ):
            continue

        relative_path = path.relative_to(PROJECT_ROOT)

        project_files.append(
            str(relative_path)
        )

    return sorted(project_files)


@mcp.tool()
def read_project_file(
    relative_path: str,
) -> str:
    """
    Διαβάζει ένα text file μέσα από το project.

    Το path πρέπει να είναι relative ως προς το project root.

    Παράδειγμα:
        src/data/pipeline.py
    """

    requested_path = (
        PROJECT_ROOT / relative_path
    ).resolve()

    try:
        requested_path.relative_to(PROJECT_ROOT)

    except ValueError:
        raise ValueError(
            "Requested path is outside the project root."
        )

    if not requested_path.exists():
        raise FileNotFoundError(
            f"File not found: {relative_path}"
        )

    if not requested_path.is_file():
        raise ValueError(
            f"Path is not a file: {relative_path}"
        )

    return requested_path.read_text(
        encoding="utf-8",
    )

app = mcp.streamable_http_app(
    transport_security=transport_security,
)