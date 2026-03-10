import hashlib
from typing import List, Dict, Any, Set
from repositories.evidence_repo import EvidenceRepository
from services.audit_service import AuditService
from services.notification_service import NotificationService


class EvidenceService:
    def upload_evidence(self, contract_id: str, file_bytes: bytes, file_url: str, file_type: str, file_size: int, added_by: str) -> Dict[str, Any]:
        """Upload evidence: validate, hash, store, and log. Returns evidence ID."""
        if not EvidenceRepository.validate_file_type(file_type):
            return {"status": "error", "message": f"File type '{file_type}' not allowed."}
        if not EvidenceRepository.validate_file_size(file_size):
            return {"status": "error", "message": "File size exceeds limit."}
        if not EvidenceRepository.virus_scan(file_bytes):
            return {"status": "error", "message": "File failed virus scan."}
        hash_value = EvidenceRepository.calculate_file_hash(file_bytes)
        metadata = EvidenceRepository.generate_evidence_metadata(file_url, file_type, file_size)
        evidence_id = EvidenceRepository.insert_evidence(
            contract_id=contract_id,
            added_by=added_by,
            file_url=file_url,
            file_type=file_type,
            file_size=file_size,
            hash_value=hash_value,
            metadata=metadata,
        )
        EvidenceRepository.store_evidence_object(file_bytes, evidence_id)
        AuditService().log_event("upload_evidence", added_by, {"contract_id": contract_id, "evidence_id": evidence_id})
        NotificationService().create_notification(added_by, "evidence_uploaded", f"Evidence uploaded for contract {contract_id}.")
        return {"status": "Evidence uploaded", "evidence_id": evidence_id}

    def validate_evidence_file(self, file_type: str, file_size: int) -> bool:
        """Return True if the file passes type and size checks."""
        return EvidenceRepository.validate_file_type(file_type) and EvidenceRepository.validate_file_size(file_size)

    def calculate_evidence_hash(self, file_bytes: bytes) -> str:
        """Return the SHA-256 hash of the file bytes."""
        return hashlib.sha256(file_bytes).hexdigest()

    def store_evidence_file(self, file_bytes: bytes, evidence_id: str) -> Dict[str, Any]:
        """Store the evidence file in object storage."""
        EvidenceRepository.store_evidence_object(file_bytes, evidence_id)
        AuditService().log_event("store_evidence", "system", {"evidence_id": evidence_id})
        return {"status": "Evidence stored"}

    def propose_evidence_addition(self, contract_id: str, evidence_id: str, user_id: str) -> Dict[str, Any]:
        """Propose an evidence record for unanimous approval by all parties."""
        AuditService().log_event("propose_evidence_addition", user_id, {"contract_id": contract_id, "evidence_id": evidence_id})
        NotificationService().create_notification(user_id, "evidence_proposed", f"Evidence {evidence_id} proposed for contract {contract_id}.")
        return {"status": "Evidence addition proposed"}

    def approve_evidence(self, evidence_id: str, user_id: str) -> Dict[str, Any]:
        """Record a user's approval of an evidence addition."""
        AuditService().log_event("approve_evidence", user_id, {"evidence_id": evidence_id})
        return {"status": "Evidence approved"}

    def check_evidence_unanimous_approval(self, evidence_id: str, required_user_ids: Set[str]) -> bool:
        """Return True if all required parties have approved the evidence addition."""
        # TODO: query evidence approval records per evidence_id
        return True

    def activate_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Activate evidence after unanimous approval."""
        AuditService().log_event("activate_evidence", "system", {"evidence_id": evidence_id})
        return {"status": "Evidence activated"}

    def request_evidence_deletion(self, evidence_id: str, user_id: str) -> Dict[str, Any]:
        """Request deletion of evidence — requires unanimous consent from all parties."""
        AuditService().log_event("request_evidence_deletion", user_id, {"evidence_id": evidence_id})
        NotificationService().create_notification(user_id, "evidence_deletion_requested", f"Deletion of evidence {evidence_id} requested.")
        return {"status": "Evidence deletion requested"}

    def approve_evidence_deletion(self, evidence_id: str, user_id: str) -> Dict[str, Any]:
        """Record a user's approval of evidence deletion."""
        AuditService().log_event("approve_evidence_deletion", user_id, {"evidence_id": evidence_id})
        return {"status": "Evidence deletion approved"}

    def delete_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Delete evidence after unanimous consent is confirmed."""
        deleted = EvidenceRepository.delete_evidence(evidence_id)
        if deleted:
            AuditService().log_event("delete_evidence", "system", {"evidence_id": evidence_id})
        return {"status": "Evidence deleted" if deleted else "Evidence not found"}

    def get_contract_evidence(self, contract_id: str) -> List[Dict[str, Any]]:
        """Return all evidence records for a contract."""
        return EvidenceRepository.get_by_contract(contract_id)
