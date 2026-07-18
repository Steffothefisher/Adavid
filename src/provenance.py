"""
ADAVID v4.0 — Clinical Trial Audit Engine
Licensed under AGPL v3 (see LICENSE). Copyright (c) 2026 ADAVID Contributors.

This module provides structures and manager classes for tracking dataset provenance
and storing/loading reproducible snapshots with cryptographic integrity checks.
"""

from __future__ import annotations

import hashlib
import json
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd


@dataclass
class DatasetProvenance:
    """Cryptographic and contextual metadata tracking the source of a dataset."""
    source: str
    query: str
    timestamp: float
    row_count: int
    data_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "query": self.query,
            "timestamp": self.timestamp,
            "row_count": self.row_count,
            "data_hash": self.data_hash,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> DatasetProvenance:
        return cls(
            source=d.get("source", "unknown"),
            query=d.get("query", ""),
            timestamp=d.get("timestamp", 0.0),
            row_count=d.get("row_count", 0),
            data_hash=d.get("data_hash", ""),
            metadata=d.get("metadata", {})
        )


@dataclass
class Snapshot:
    """An immutable bundle of clinical data and its verified provenance."""
    data: pd.DataFrame
    provenance: DatasetProvenance


class SnapshotManager:
    """Manager to create, save, and load datasets with strict integrity checks."""

    def __init__(self, storage_dir: str = "./snapshots"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def calculate_hash(df: pd.DataFrame) -> str:
        """Computes a stable SHA-256 hash of the DataFrame's CSV representation."""
        # Convert to CSV string with sorted column names to ensure stable hashes
        sorted_df = df.reindex(sorted(df.columns), axis=1)
        csv_data = sorted_df.to_csv(index=False, lineterminator="\n").encode("utf-8")
        return hashlib.sha256(csv_data).hexdigest()

    def create_snapshot(
        self, 
        df: pd.DataFrame, 
        source: str, 
        query: str = "", 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Snapshot:
        """Creates a Snapshot object with current timestamp and data hash."""
        data_hash = self.calculate_hash(df)
        provenance = DatasetProvenance(
            source=source,
            query=query,
            timestamp=time.time(),
            row_count=len(df),
            data_hash=data_hash,
            metadata=metadata or {}
        )
        return Snapshot(data=df.copy(), provenance=provenance)

    def save_snapshot(self, snapshot: Snapshot, filename: str) -> Path:
        """
        Saves the snapshot into a zipped archive containing the data CSV
        and the provenance metadata JSON.
        """
        if not filename.endswith(".zip"):
            filename += ".zip"
        
        file_path = self.storage_dir / filename
        
        # Sort columns to ensure consistent written form matching the hash
        sorted_df = snapshot.data.reindex(sorted(snapshot.data.columns), axis=1)
        csv_string = sorted_df.to_csv(index=False, lineterminator="\n")
        provenance_json = json.dumps(snapshot.provenance.to_dict(), indent=2)

        with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("data.csv", csv_string)
            zf.writestr("provenance.json", provenance_json)

        return file_path

    def load_snapshot(self, filename: str) -> Snapshot:
        """
        Loads and cryptographically validates a snapshot archive.
        Raises ValueError if the data has been altered or tampered with.
        """
        if not filename.endswith(".zip"):
            filename += ".zip"
            
        file_path = self.storage_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Snapshot file not found: {file_path}")

        with zipfile.ZipFile(file_path, "r") as zf:
            provenance_bytes = zf.read("provenance.json")
            provenance_dict = json.loads(provenance_bytes.decode("utf-8"))
            provenance = DatasetProvenance.from_dict(provenance_dict)

            # Load CSV data
            with zf.open("data.csv") as csv_file:
                df = pd.read_csv(csv_file)

        # Verify integrity
        recalculated_hash = self.calculate_hash(df)
        if recalculated_hash != provenance.data_hash:
            raise ValueError(
                f"CRITICAL INTEGRITY FAILURE: Dataset hash mismatch!\n"
                f"Expected: {provenance.data_hash}\n"
                f"Computed: {recalculated_hash}"
            )

        return Snapshot(data=df, provenance=provenance)
