import os
from typing import Optional

"""Configuration loader for environment-based settings.

This module attempts to load environment variables from a project-level .env
file first. As a convenience for some dev setups, it also falls back to
loading a .env inside the local virtual environment directory (venv/.env)
if the primary .env is not present or doesn't define the needed variables.
"""

# Load the .env from project root, even if CWD is app/
try:
    from dotenv import load_dotenv, find_dotenv

    # 1) Try to load the nearest .env (typically project root)
    load_dotenv(find_dotenv(), override=True)

    # 2) If GROQ_API_KEY is still missing, try venv/.env as a fallback
    if not os.getenv("GROQ_API_KEY"):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        venv_env_path = os.path.join(project_root, "venv", ".env")
        if os.path.exists(venv_env_path):
            load_dotenv(venv_env_path, override=True)
except Exception:
    # If python-dotenv isn't available or any error occurs, we continue and
    # rely on environment variables being set by the runtime environment.
    pass

# (optional) Bridge Streamlit secrets → env
try:
    import streamlit as st  # type: ignore
    if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets and not os.getenv("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
