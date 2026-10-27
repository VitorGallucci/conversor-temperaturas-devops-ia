"""Gera um pacote executável com Python, sem ferramentas externas de build."""

import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
destination = root / "build/package"
destination.mkdir(parents=True, exist_ok=True)
for name in ("conversor", "web"):
    shutil.copytree(
        root / name,
        destination / name,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
shutil.copy2(root / "README.md", destination / "README.md")
archive = shutil.make_archive(str(root / "dist/conversor"), "zip", destination)
print(archive)
