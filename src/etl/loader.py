"""Sprint 1 ETL loader.

Loads the workbook sources into the SQLite database defined by db/schema.sql,
normalises the key fields, removes duplicates, and writes load_audit.csv.
"""

from __future__ import annotations

import csv
import logging
import logging.config
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml
from dotenv import load_dotenv

from src.etl.normaliser import apply_normalisation

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "nifty100.db"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "output"
DEFAULT_SCHEMA_PATH = ROOT_DIR / "db" / "schema.sql"

TABLE_SPECS: dict[str, tuple[Path, int]] = {
    "companies": (ROOT_DIR / "data" / "raw" / "companies.xlsx", 1),
    "profitandloss": (ROOT_DIR / "data" / "raw" / "profitandloss.xlsx", 1),
    "balancesheet": (ROOT_DIR / "data" / "raw" / "balancesheet.xlsx", 1),
    "cashflow": (ROOT_DIR / "data" / "raw" / "cashflow.xlsx", 1),
    "analysis": (ROOT_DIR / "data" / "raw" / "analysis.xlsx", 1),
    "documents": (ROOT_DIR / "data" / "raw" / "documents.xlsx", 1),
    "prosandcons": (ROOT_DIR / "data" / "raw" / "prosandcons.xlsx", 1),
    "sectors": (ROOT_DIR / "data" / "supporting" / "sectors.xlsx", 0),
    "stock_prices": (ROOT_DIR / "data" / "supporting" / "stock_prices.xlsx", 0),
    "market_cap": (ROOT_DIR / "data" / "supporting" / "market_cap.xlsx", 0),
    "financial_ratios": (ROOT_DIR / "data" / "supporting" / "financial_ratios.xlsx", 0),
    "peer_groups": (ROOT_DIR / "data" / "supporting" / "peer_groups.xlsx", 0),
}

LOAD_ORDER: tuple[str, ...] = (
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "sectors",
    "stock_prices",
    "market_cap",
    "financial_ratios",
    "peer_groups",
)

BAD_TICKER_VALUES = {"", "MISSING", "INVALID", "PARSE_ERROR", "NAN", "NONE"}

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadRecord:
    table: str
    source_file: str
    rows_in: int
    rows_out: int
    duplicates_removed: int
    rejected: int
    status: str
    message: str = ""
    runtime_s: float = 0.0
    timestamp: str = ""


def configure_logging() -> None:
    """Load the project logging config if available, otherwise use basic logging."""

    config_path = ROOT_DIR / "config" / "logging_config.yaml"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            logging.config.dictConfig(yaml.safe_load(handle))
        return
    logging.basicConfig(level=logging.INFO)


def _resolve_path(value: str, default: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT_DIR / path if str(path) else default


def discover_source_files(directory: Path, filenames: Iterable[str]) -> list[Path]:
    """Return the source files that are present in ``directory``."""

    return [directory / filename for filename in filenames if (directory / filename).exists()]


def load_workbook(path: Path, header_row: int) -> pd.DataFrame:
    """Load a workbook with the configured header row."""

    frame = pd.read_excel(path, header=header_row, engine="openpyxl")
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def _dedupe_keys(table_name: str) -> list[str]:
    return {
        "companies": ["id"],
        "profitandloss": ["company_id", "year"],
        "balancesheet": ["company_id", "year"],
        "cashflow": ["company_id", "year"],
        "analysis": ["id"],
        "documents": ["id"],
        "prosandcons": ["id"],
        "sectors": ["company_id"],
        "stock_prices": ["company_id", "date"],
        "market_cap": ["company_id", "year"],
        "financial_ratios": ["company_id", "year"],
        "peer_groups": ["company_id", "peer_group_name"],
    }.get(table_name, [])


def deduplicate(frame: pd.DataFrame, table_name: str) -> tuple[pd.DataFrame, int]:
    keys = _dedupe_keys(table_name)
    before = len(frame)
    if keys:
        frame = frame.drop_duplicates(subset=keys, keep="last").copy()
    else:
        frame = frame.drop_duplicates().copy()
    return frame, before - len(frame)


def filter_bad_tickers(frame: pd.DataFrame, table_name: str) -> tuple[pd.DataFrame, int]:
    if frame.empty:
        return frame.copy(), 0

    mask = pd.Series(False, index=frame.index)
    if "company_id" in frame.columns:
        mask = mask | frame["company_id"].astype(str).str.strip().str.upper().isin(BAD_TICKER_VALUES)
    if table_name == "companies" and "id" in frame.columns:
        mask = mask | frame["id"].astype(str).str.strip().str.upper().isin(BAD_TICKER_VALUES)
    if "year" in frame.columns:
        mask = mask | frame["year"].astype(str).str.strip().eq("PARSE_ERROR")
    if "Year" in frame.columns:
        mask = mask | frame["Year"].isna()
    rejected = int(mask.sum())
    return frame.loc[~mask].copy(), rejected


def filter_orphan_company_ids(frame: pd.DataFrame, table_name: str, parent_ids: set[str]) -> tuple[pd.DataFrame, int]:
    if frame.empty or "company_id" not in frame.columns or not parent_ids:
        return frame.copy(), 0

    values = frame["company_id"].astype(str).str.strip().str.upper()
    mask = ~values.isin(parent_ids)
    rejected = int(mask.sum())
    return frame.loc[~mask].copy(), rejected


def _write_audit_csv(records: list[LoadRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "table",
                "source_file",
                "rows_in",
                "rows_out",
                "duplicates_removed",
                "rejected",
                "status",
                "message",
                "runtime_s",
                "timestamp",
            ],
        )
        writer.writeheader()
        writer.writerows(record.__dict__ for record in records)


def _load_schema(conn: sqlite3.Connection) -> None:
    if DEFAULT_SCHEMA_PATH.exists():
        conn.executescript(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8"))


def _prepare_frame(frame: pd.DataFrame, table_name: str) -> pd.DataFrame:
    frame = apply_normalisation(frame, table_name)
    if table_name in {"sectors", "stock_prices", "market_cap", "financial_ratios", "peer_groups"}:
        frame = frame.drop(columns=["id"], errors="ignore")
    if table_name == "documents" and "Year" in frame.columns:
        frame["Year"] = pd.to_numeric(frame["Year"], errors="coerce").astype("Int64")
    if table_name == "peer_groups" and "is_benchmark" in frame.columns:
        frame["is_benchmark"] = pd.to_numeric(frame["is_benchmark"], errors="coerce").fillna(0).astype("Int64")
    return frame


def load_table(conn: sqlite3.Connection, table_name: str, file_path: Path, header_row: int) -> LoadRecord:
    start = datetime.now()
    frame = load_workbook(file_path, header_row)
    rows_in = len(frame.index)
    frame = _prepare_frame(frame, table_name)
    frame, duplicates_removed = deduplicate(frame, table_name)
    frame, rejected = filter_bad_tickers(frame, table_name)

    parent_ids: set[str] = set()
    if table_name != "companies" and "company_id" in frame.columns:
        parent_frame = pd.read_sql_query("SELECT id FROM companies", conn)
        parent_ids = set(parent_frame["id"].astype(str).str.strip().str.upper().tolist())
        frame, orphan_rejected = filter_orphan_company_ids(frame, table_name, parent_ids)
        rejected += orphan_rejected

    rows_out = len(frame.index)
    frame.to_sql(table_name, conn, if_exists="append", index=False)
    runtime_s = round((datetime.now() - start).total_seconds(), 3)
    return LoadRecord(
        table=table_name,
        source_file=file_path.name,
        rows_in=rows_in,
        rows_out=rows_out,
        duplicates_removed=duplicates_removed,
        rejected=rejected,
        status="loaded",
        runtime_s=runtime_s,
        timestamp=datetime.now().isoformat(),
    )


def build_database(db_path: Path, output_dir: Path) -> list[LoadRecord]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        _load_schema(conn)

        audit: list[LoadRecord] = []
        for table_name in LOAD_ORDER:
            file_path, header_row = TABLE_SPECS[table_name]
            audit.append(load_table(conn, table_name, file_path, header_row))

        conn.commit()
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise SystemExit(f"{len(violations)} foreign key violation(s) found")

    _write_audit_csv(audit, output_dir / "load_audit.csv")
    return audit


def main() -> int:
    load_dotenv()
    configure_logging()
    db_path = _resolve_path(os.getenv("DB_PATH", str(DEFAULT_DB_PATH)), DEFAULT_DB_PATH)
    output_dir = _resolve_path(os.getenv("OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)), DEFAULT_OUTPUT_DIR)
    audit = build_database(db_path, output_dir)
    logger.info("ETL complete | tables=%d | rows=%d", len(audit), sum(record.rows_out for record in audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
