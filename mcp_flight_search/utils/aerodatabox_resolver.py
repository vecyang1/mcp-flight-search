"""
1Password & Environment Credential Resolver for AeroDataBox (RapidAPI).
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

DEFAULT_1P_AERODATABOX_REF = os.environ.get(
    "AERODATABOX_1P_REF",
    "op://Agent Automation/AeroDataBox API Key - RapidAPI (Flight Data)/credential",
)
FALLBACK_1P_ITEM_ID_REF = "op://Agent Automation/4yoyezeykzvblmlu7kc3pce3pm/credential"


def _read_from_1password(reference: str, timeout_sec: float = 3.5) -> Optional[str]:
    """Read secret via 1Password CLI using op read --no-newline."""
    op_path = shutil.which("op")
    if not op_path:
        return None
    try:
        proc = subprocess.run(
            [op_path, "read", reference, "--no-newline"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except Exception:
        pass
    return None


def _read_from_dotenv(env_path: Path) -> Optional[str]:
    """Parse AERODATABOX_API_KEY or RAPIDAPI_KEY from a .env file."""
    if not env_path.is_file():
        return None
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k in ("AERODATABOX_API_KEY", "RAPIDAPI_KEY", "RAPID_API_KEY"):
                        return v
    except Exception:
        pass
    return None


def resolve_aerodatabox_key(custom_key: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Resolve AeroDataBox / RapidAPI API key.
    Returns: (api_key, source_description)
    """
    if custom_key:
        return custom_key, "explicit_arguments"

    # 1. Environment variables
    for env_var in ("AERODATABOX_API_KEY", "RAPIDAPI_KEY", "RAPID_API_KEY"):
        val = os.environ.get(env_var)
        if val and val.strip():
            return val.strip(), f"environment_variable:{env_var}"

    # 2. 1Password item reference
    key_1p = _read_from_1password(DEFAULT_1P_AERODATABOX_REF) or _read_from_1password(FALLBACK_1P_ITEM_ID_REF)
    if key_1p:
        return key_1p, "1password_vault"

    # 3. Local skill .env
    skill_env = Path(__file__).resolve().parent.parent.parent / ".env"
    key_dotenv = _read_from_dotenv(skill_env)
    if key_dotenv:
        return key_dotenv, f"dotenv_file:{skill_env}"

    return None, "missing_credentials"
