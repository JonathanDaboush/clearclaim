# ExportController calls ExportService
from typing import Dict, Any, List
from services.export_service import ExportService

export_service = ExportService()

def export_contract_history(contract_id: str) -> Dict[str, Any]:
    """Controller for exporting contract history."""
    return export_service.export_contract_history(contract_id)

def export_contract_versions(contract_id: str) -> List[Dict[str, Any]]:
    """Controller for exporting contract versions."""
    return export_service.export_contract_versions(contract_id)

def export_contract_signatures(contract_id: str) -> List[Dict[str, Any]]:
    """Controller for exporting contract signatures."""
    return export_service.export_contract_signatures(contract_id)

def export_contract_evidence(contract_id: str) -> List[Dict[str, Any]]:
    """Controller for exporting contract evidence."""
    return export_service.export_contract_evidence(contract_id)

def export_audit_logs(contract_id: str) -> List[Dict[str, Any]]:
    """Controller for exporting audit logs."""
    return export_service.export_audit_logs(contract_id)

def build_case_archive(contract_id: str) -> Dict[str, Any]:
    """Controller for building case archive."""
    return export_service.build_case_archive(contract_id)
