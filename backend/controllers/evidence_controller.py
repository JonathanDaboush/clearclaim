# EvidenceController handler functions for evidence pipeline
# EvidenceController calls EvidenceService
from services.evidence_service import EvidenceService

evidence_service = EvidenceService()

def upload_evidence(contract_id, file, user_id):
    """Controller for uploading evidence."""
    return evidence_service.upload_evidence(contract_id, file, user_id)

def validate_evidence_file(file):
    """Controller for validating evidence file."""
    return evidence_service.validate_evidence_file(file)

def calculate_evidence_hash(file):
    """Controller for calculating evidence hash."""
    return evidence_service.calculate_evidence_hash(file)

def store_evidence_file(file):
    """Controller for storing evidence file."""
    return evidence_service.store_evidence_file(file)

def propose_evidence_addition(contract_id, evidence_id, user_id):
    """Controller for proposing evidence addition."""
    return evidence_service.propose_evidence_addition(contract_id, evidence_id, user_id)

def approve_evidence(evidence_id, user_id):
    """Controller for approving evidence."""
    return evidence_service.approve_evidence(evidence_id, user_id)

def check_evidence_unanimous_approval(evidence_id):
    """Controller for checking evidence unanimous approval."""
    return evidence_service.check_evidence_unanimous_approval(evidence_id)

def activate_evidence(evidence_id):
    """Controller for activating evidence."""
    return evidence_service.activate_evidence(evidence_id)

def request_evidence_deletion(evidence_id, user_id):
    """Controller for requesting evidence deletion."""
    return evidence_service.request_evidence_deletion(evidence_id, user_id)

def approve_evidence_deletion(evidence_id, user_id):
    """Controller for approving evidence deletion."""
    return evidence_service.approve_evidence_deletion(evidence_id, user_id)

def delete_evidence(evidence_id):
    """Controller for deleting evidence."""
    return evidence_service.delete_evidence(evidence_id)

def get_contract_evidence(contract_id):
    """Controller for getting contract evidence."""
    return evidence_service.get_contract_evidence(contract_id)
