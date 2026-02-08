"""
Token optimisation utilities.

This module defines helper functions for reducing the number of tokens
sent to large language models.  Strategies include truncating the
conversation history to the last `k` exchanges and extracting minimal
context from source files.

These functions are not yet integrated into the orchestrator, but
provide a foundation for further optimisation work.
"""

from __future__ import annotations

from typing import List, Dict, Any


def truncate_history(history: List[Dict[str, str]], max_pairs: int = 2) -> List[Dict[str, str]]:
    """Return only the most recent message pairs from a chat history.

    Parameters
    ----------
    history : list of dict
        Each dict should have a 'role' and 'content' key.
    max_pairs : int
        Maximum number of user/assistant pairs to keep.

    Returns
    -------
    list of dict
        Truncated history containing at most `max_pairs * 2` messages.
    """
    # count pairs by looking for user messages
    user_indices = [i for i, msg in enumerate(history) if msg.get("role") == "user"]
    # keep last max_pairs user messages and everything after them
    if len(user_indices) <= max_pairs:
        return history
    cut_index = user_indices[-max_pairs]
    return history[cut_index:]


def extract_diff(original: str, modified: str, context_lines: int = 3) -> str:
    """Produce a minimal diff between two strings.

    Returns a unified diff with a small context, suitable for sending to
    review agents.  This is a simple line‑by‑line comparison and does
    not rely on external libraries.
    """
    import difflib
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile="original",
        tofile="modified",
        lineterm="",
        n=context_lines,
    )
    return "".join(list(diff))