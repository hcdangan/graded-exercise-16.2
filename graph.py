"""LangGraph Studio entry point for the Week 16 research assistant.

The notebook is the source of truth for the graph: the tools, nodes and graph
wiring live in ``week16_HarleyDangan_lab_research_agent.ipynb``. To avoid
maintaining a second copy of that code, this module replays the notebook's code
cells (everything except the demo "Run The Graph" cell) and exposes the
compiled application as ``graph``.

Start the local server with:

    uv run --env-file .env langgraph dev --allow-blocking

``--allow-blocking`` is required because the nodes call synchronous libraries
(guardrails, requests, the arXiv client, and the web-search-free CLI).

Web search calls the free ``web-search-free`` skill CLI, so no paid search
API is used: set ``WEB_SEARCH_FREE_SKILL_PATH`` in ``.env`` to the installed
skill directory. Every search is live; there is no mock mode.

``langgraph dev`` only watches Python files, so restart the server (or touch
this file) after editing the notebook.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType

from dotenv import load_dotenv

NOTEBOOK_PATH = Path(__file__).with_name("week16_HarleyDangan_lab_research_agent.ipynb")
MODULE_NAME = "week16_research_agent"

# The CLI also loads the "env" entry from langgraph.json; doing it here keeps
# plain ``import graph`` working outside the CLI as well.
load_dotenv(NOTEBOOK_PATH.parent / ".env", override=False)


def _is_demo_cell(source: str) -> bool:
    """Return True for notebook cells that run or print the compiled graph.

    Comment lines are ignored so the question-node cell's commented
    ``app.invoke`` example is not mistaken for a demo cell.
    """
    executable = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    return "app.invoke(" in executable or "print_ascii(" in executable


def _build_graph():
    """Execute the notebook's code cells in a real module and return ``app``."""
    if not NOTEBOOK_PATH.exists():
        raise FileNotFoundError(f"Notebook not found: {NOTEBOOK_PATH}")

    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    # A real module (registered in sys.modules) is required because typing uses
    # ``AgentState.__module__`` to resolve its annotations (Annotated, add_messages).
    module = ModuleType(MODULE_NAME)
    module.__file__ = str(NOTEBOOK_PATH)
    module.__dict__["__builtins__"] = __builtins__
    sys.modules[MODULE_NAME] = module
    namespace = module.__dict__

    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue

        source = "".join(cell["source"])
        if _is_demo_cell(source):
            # Running the demo cell at import time would invoke the graph.
            continue

        filename = f"{NOTEBOOK_PATH.name}:{cell['id']}"
        exec(compile(source, filename, "exec"), namespace)

    # The notebook names the StateGraph "graph" and the compiled app "app".
    return namespace.get("app") or namespace["graph"]


graph = _build_graph()

__all__ = ["graph"]
