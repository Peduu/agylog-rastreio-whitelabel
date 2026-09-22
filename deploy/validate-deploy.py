from __future__ import annotations

import pathlib
import py_compile
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "deploy" / "deploy-manifest.tsv"
ALLOWED_TARGET_PREFIXES = ("/home/rastreamento/",)
FORBIDDEN_SOURCE_PARTS = (
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "backups",
    "importacoes",
    "instance",
)
FORBIDDEN_SOURCE_SUFFIXES = (
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".xlsx",
    ".xls",
    ".csv",
    ".pyc",
    ".pyo",
)
FORBIDDEN_NAME_MARKERS = (
    ".bak",
    ".bk",
    "backup",
    ".urlfix-",
    ".codexbak-",
)


def fail(message: str) -> None:
    print(f"ERRO: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_manifest() -> list[tuple[str, str]]:
    if not MANIFEST.exists():
        fail("deploy/deploy-manifest.tsv nao encontrado")

    entries: list[tuple[str, str]] = []
    for lineno, raw in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) != 2:
            fail(f"manifesto linha {lineno}: use exatamente source<TAB>target")
        source, target = parts[0].strip(), parts[1].strip()
        if not source or not target:
            fail(f"manifesto linha {lineno}: source/target vazio")
        entries.append((source, target))
    if not entries:
        fail("manifesto vazio")
    return entries


def validate_manifest(entries: list[tuple[str, str]]) -> None:
    seen_targets: set[str] = set()
    for source, target in entries:
        pure_source = pathlib.PurePosixPath(source)
        if source.startswith("/") or ".." in pure_source.parts:
            fail(f"source invalido no manifesto: {source}")
        if not target.startswith(ALLOWED_TARGET_PREFIXES):
            fail(f"target fora das areas permitidas: {target}")
        if target in seen_targets:
            fail(f"target duplicado no manifesto: {target}")
        seen_targets.add(target)

        lowered_parts = tuple(part.lower() for part in pure_source.parts)
        lowered_name = pure_source.name.lower()
        if any(part in lowered_parts for part in FORBIDDEN_SOURCE_PARTS):
            fail(f"source proibido no manifesto: {source}")
        if lowered_name.endswith(FORBIDDEN_SOURCE_SUFFIXES):
            fail(f"tipo de arquivo proibido no manifesto: {source}")
        if any(marker in lowered_name for marker in FORBIDDEN_NAME_MARKERS):
            fail(f"arquivo de backup proibido no manifesto: {source}")

        path = ROOT / source
        if not path.is_file():
            fail(f"arquivo do manifesto nao existe: {source}")


def validate_python() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        for path in ROOT.glob("*.py"):
            py_compile.compile(str(path), cfile=str(tmp / f"{path.name}.pyc"), doraise=True)


def validate_env_example() -> None:
    env_example = ROOT / ".env.example"
    if not env_example.exists():
        fail(".env.example ausente")
    text = env_example.read_text(encoding="utf-8")
    for forbidden in ("TMS_API_TOKEN=", "SECRET_KEY=", "INTERLOG_API_TOKEN="):
        for line in text.splitlines():
            if line.startswith(forbidden) and line.strip() != forbidden:
                fail(f".env.example contem valor real em {forbidden.rstrip('=')}")


def main() -> None:
    entries = read_manifest()
    validate_manifest(entries)
    validate_python()
    validate_env_example()
    print("Validacao local OK")
    for source, target in entries:
        print(f"  {source} -> {target}")


if __name__ == "__main__":
    main()
