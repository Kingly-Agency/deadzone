from __future__ import annotations

import os
import secrets
from pathlib import Path

from pydantic import BaseModel

from app.domain.models import Mode


class Settings(BaseModel):
    version: str = "0.1.0"
    mode: Mode = "ble"
    seed: int = 1337
    data_dir: Path
    capture_salt: str
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
    ]

    @property
    def capture_dir(self) -> Path:
        return self.data_dir / "captures"


def load_settings() -> Settings:
    backend_root = Path(__file__).resolve().parents[1]
    data_dir = Path(os.environ.get("DEADZONE_DATA_DIR", backend_root / "data"))
    return Settings(
        mode=os.environ.get("DEADZONE_MODE", "ble"),  # type: ignore[arg-type]
        seed=int(os.environ.get("DEADZONE_SEED", "1337")),
        data_dir=data_dir,
        capture_salt=_capture_salt(data_dir),
    )


def _capture_salt(data_dir: Path) -> str:
    configured = os.environ.get("DEADZONE_CAPTURE_SALT")
    if configured:
        return configured
    data_dir.mkdir(parents=True, exist_ok=True)
    salt_path = data_dir / ".capture_salt"
    if salt_path.exists():
        return salt_path.read_text(encoding="utf-8").strip()
    salt = secrets.token_hex(32)
    salt_path.write_text(salt, encoding="utf-8")
    return salt
