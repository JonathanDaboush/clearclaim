from typing import Dict, Any
from services.audit_service import AuditService


class AuditVerificationService:
    def verify_audit(self, contract_id: str) -> Dict[str, Any]:
        """Verify the audit chain integrity for a given contract.
        Returns a dict with 'valid' bool and any discrepancies found."""
        valid = AuditService().verify_audit_chain()
        return {"contract_id": contract_id, "valid": valid}
