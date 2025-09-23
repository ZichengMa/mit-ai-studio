#!/usr/bin/env python3
"""
NANDA adapter for MitAiStudio (CrewAI project).

Expose your CrewAI flows via NANDA's HTTP API so the agent becomes
discoverable and interoperable on the public internet.

Env vars:
- OPENAI_API_KEY       CrewAI agents (if using OpenAI models)
- ANTHROPIC_API_KEY    NANDA bridge enrollment/registry
- DOMAIN_NAME          Your domain pointing to this EC2 instance (for SSL)

Certs:
Place `fullchain.pem` and `privkey.pem` in the current working directory
you use to start this process (NANDA will read them there).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

from nanda_adapter import NANDA


def _project_root() -> Path:
    # This file: <root>/src/mit_ai_studio/nanda_bridge.py
    # Project root is parent of src.
    return Path(__file__).resolve().parents[2]


def _load_user_pref() -> str:
    # knowledge/user_preference.txt lives at project root level
    path = _project_root() / "knowledge" / "user_preference.txt"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def create_mit_ai_studio_improvement() -> Callable[[str], str]:
    """Returns a callable that routes inbound messages to the Crew.

    Routing rules:
    - Contains "self introduction" (case-insensitive) -> intro_task
    - Starts with "brewing:" (case-insensitive) -> research_task + brew_task
    - Otherwise -> research_task only
    """
    # Ensure project src/ is on sys.path when executed via `python src/.../nanda_bridge.py`
    src_path = _project_root() / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from mit_ai_studio.crew import MitAiStudio

    def run_with_crewai(message_text: str) -> str:
        message = (message_text or "").strip()
        now_year = str(datetime.now().year)

        if "self introduction" in message.lower():
            tasks = ("intro_task",)
        elif message.lower().startswith("brewing:"):
            tasks = ("research_task", "brew_task")
        else:
            tasks = ("research_task",)

        inputs = {
            "topic": message if message else "AI LLMs",
            "current_year": now_year,
            "user_preference": _load_user_pref(),
        }

        crew = MitAiStudio().crew(tasks=tasks)
        result = crew.kickoff(inputs=inputs)
        return str(result)

    return run_with_crewai


def main() -> None:
    # Build improvement function backed by your CrewAI logic
    improvement = create_mit_ai_studio_improvement()

    # Read NANDA config
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    domain = os.getenv("DOMAIN_NAME")

    if not anthropic_key or not domain:
        print(
            "ERROR: Missing ANTHROPIC_API_KEY or DOMAIN_NAME. "
            "Export them and ensure SSL certs (fullchain.pem/privkey.pem) are in CWD.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Start NANDA server (looks for certs in current directory)
    nanda = NANDA(improvement)
    nanda.start_server_api(anthropic_key, domain)


if __name__ == "__main__":
    main()
