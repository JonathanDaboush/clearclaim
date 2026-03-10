# EvidenceController handler functions for evidence pipeline
# EvidenceController calls EvidenceService
from typing import Dict, Any, List, Set
from services.evidence_service import EvidenceService

evidence_service = EvidenceService()

def upload_evidence(contract_id: str, file_bytes: bytes, file_url: str, file_type: str, file_size: int, added_by: str) -> Dict[str, Any]:
    """Controller for uploading evidence."""
    return evidence_service.upload_evidence(contract_id, file_bytes, file_url, file_type, file_size, added_by)

def validate_evidence_file(file_type: str, file_size: int) -> bool:
    """Controller for validating evidence file."""
    return evidence_service.validate_evidence_file(file_type, file_size)

def calculate_evidence_hash(file_bytes: bytes) -> str:
    """Controller for calculating evidence hash."""
    return evidence_service.calculate_evidence_hash(file_bytes)

def store_evidence_file(file_bytes: bytes, evidence_id: str) -> Dict[str, Any]:
    """Controller for storing evidence file."""
    return evidence_service.store_evidence_file(file_bytes, evidence_id)

def propose_evidence_addition(contract_id: str, evidence_id: str, user_id: str) -> Dict[str, Any]:
    """Controller for proposing evidence addition."""
    return evidence_service.propose_evidence_addition(contract_id, evidence_id, user_id)

def approve_evidence(evidence_id: str, user_id: str) -> Dict[str, Any]:
    """Controller for approving evidence."""
    return evidence_service.approve_evidence(evidence_id, user_id)

def check_evidence_unanimous_approval(evidence_id: str, required_user_ids: Set[str]) -> bool:
    """Controller for checking evidence unanimous approval."""
    return evidence_service.check_evidence_unanimous_approval(evidence_id, required_user_ids)

def activate_evidence(evidence_id: str) -> Dict[str, Any]:
    """Controller for activating evidence."""
    return evidence_service.activate_evidence(evidence_id)

def request_evidence_deletion(evidence_id: str, user_id: str) -> Dict[str, Any]:
    """Controller for requesting evidence deletion."""
    return evidence_service.request_evidence_deletion(evidence_id, user_id)

def approve_evidence_deletion(evidence_id: str, user_id: str) -> Dict[str, Any]:
    """Controller for approving evidence deletion."""
    return evidence_service.approve_evidence_deletion(evidence_id, user_id)

def delete_evidence(evidence_id: str) -> Dict[str, Any]:
    """Controller for deleting evidence."""
    return evidence_service.delete_evidence(evidence_id)

def get_contract_evidence(contract_id: str) -> List[Dict[str, Any]]:
    """Controller for getting contract evidence."""
    return evidence_service.get_contract_evidence(contract_id)
