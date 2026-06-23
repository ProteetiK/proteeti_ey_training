from dotenv import load_dotenv
import os

load_dotenv()

MODEL = os.getenv(
    "MODEL",
    "claude-sonnet-4-20250514"
)

ANTHROPIC_API_KEY = os.getenv(
    "ANTHROPIC_API_KEY",
    ""
)

LIVE = bool(ANTHROPIC_API_KEY)