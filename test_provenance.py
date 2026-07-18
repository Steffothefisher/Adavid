import pytest
import pandas as pd
import numpy as np
import zipfile
import json
from pathlib import Path
from src.provenance import SnapshotManager, DatasetProvenance, Snapshot


def test_hash_stability():
    """Verify that different column order produces the same SHA-256 hash."""
    df1 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    df2 = pd.DataFrame({"B": [4, 5, 6], "A": [1, 2, 3]})
    
    hash1 = SnapshotManager.calculate_hash(df1)
    hash2 = SnapshotManager.calculate_hash(df2)
    assert hash1 == hash2


def test_snapshot_creation():
    """Verify snapshot constructor correctly logs metadata and row count."""
    df = pd.DataFrame({"val": np.random.randn(10)})
    manager = SnapshotManager()
    
    snapshot = manager.create_snapshot(df, source="test_source", query="select *", metadata={"env": "test"})
    assert snapshot.provenance.source == "test_source"
    assert snapshot.provenance.query == "select *"
    assert snapshot.provenance.row_count == 10
    assert snapshot.provenance.metadata == {"env": "test"}
    assert len(snapshot.provenance.data_hash) == 64  # SHA-256 length


def test_save_and_load_cycle(tmp_path):
    """Verify saving a snapshot to zip and loading it back returns identical data."""
    df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    manager = SnapshotManager(storage_dir=str(tmp_path))
    
    snapshot = manager.create_snapshot(df, source="test_cycle")
    zip_path = manager.save_snapshot(snapshot, "test_snap.zip")
    
    assert zip_path.exists()
    
    # Load back
    loaded = manager.load_snapshot("test_snap.zip")
    pd.testing.assert_frame_equal(loaded.data, df)
    assert loaded.provenance.source == "test_cycle"
    assert loaded.provenance.data_hash == snapshot.provenance.data_hash


def test_data_tampering_detection(tmp_path):
    """Verify that any modification to the saved CSV data is caught by the hash check."""
    df = pd.DataFrame({"A": [10, 20, 30]})
    manager = SnapshotManager(storage_dir=str(tmp_path))
    
    snapshot = manager.create_snapshot(df, source="secure_source")
    zip_path = manager.save_snapshot(snapshot, "secure_snap.zip")
    
    # Programmatically tamper with the data inside the zip
    # 1. Read metadata from zip
    with zipfile.ZipFile(zip_path, "r") as z:
        prov_json = z.read("provenance.json")
    
    # 2. Write tampered CSV back
    tampered_csv = "A\n10\n20\n999\n"  # 30 replaced by 999
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("provenance.json", prov_json)
        z.writestr("data.csv", tampered_csv)
        
    # 3. Try to load snapshot and expect ValueError due to hash mismatch
    with pytest.raises(ValueError) as excinfo:
        manager.load_snapshot("secure_snap.zip")
    
    assert "CRITICAL INTEGRITY FAILURE" in str(excinfo.value)
