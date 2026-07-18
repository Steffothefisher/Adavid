"""ADAVID - Clinical Trial Audit Engine"""

try:
    from .adavid_engine import AdavidAuditEngine, AuditConfig, RiskLevel, AuditStatus
except Exception:  # pragma: no cover - optional dependency fallback
    AdavidAuditEngine = None
    AuditConfig = None
    RiskLevel = None
    AuditStatus = None

from .protocol_parser import ProtocolParser, ProtocolSpecification, PublicationSpecification, OutcomeDefinition
from .discrepancy_analyzer import DiscrepancyAnalyzer
from .publication_bias_detector import Study, PublicationBiasDetector, run_meta_analysis
from .live_data_clients import ClinicalTrialsClient, FAERSLiveClient
from .provenance import DatasetProvenance, Snapshot, SnapshotManager

__version__ = "1.0.0"
__all__ = [
    'AdavidAuditEngine',
    'AuditConfig',
    'RiskLevel',
    'AuditStatus',
    'ProtocolParser',
    'ProtocolSpecification',
    'PublicationSpecification',
    'OutcomeDefinition',
    'DiscrepancyAnalyzer',
    'Study',
    'PublicationBiasDetector',
    'run_meta_analysis',
    'ClinicalTrialsClient',
    'FAERSLiveClient',
    'DatasetProvenance',
    'Snapshot',
    'SnapshotManager',
]
