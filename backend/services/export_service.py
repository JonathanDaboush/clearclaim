from typing import List, Dict, Any, Set
from repositories.contracts_repo import ContractsRepository
from repositories.contract_versions_repo import ContractVersionsRepository
from repositories.signature_repo import SignatureRepository
from repositories.evidence_repo import EvidenceRepository
from repositories.audit_repo import AuditRepository


class ExportService:
    def export_contract_history(self, contract_id: str) -> Dict[str, Any]:
        """Export the full contract record."""
        contracts: List[Dict[str, Any]] = ContractsRepository.get_by_id(contract_id)
        return {"contract_id": contract_id, "contracts": contracts}

    def export_contract_versions(self, contract_id: str) -> List[Dict[str, Any]]:
        """Export all versions of a contract."""
        return [vars(v) for v in ContractVersionsRepository.get_by_contract(contract_id)]

    def export_contract_signatures(self, contract_id: str) -> List[Dict[str, Any]]:
        """Export all signatures associated with contract versions."""
        version_ids: Set[str] = {v.id for v in ContractVersionsRepository.get_by_contract(contract_id)}
        return [vars(s) for s in SignatureRepository.get_by_version_ids(version_ids)]

    def export_contract_evidence(self, contract_id: str) -> List[Dict[str, Any]]:
        """Export all evidence records for a contract."""
        return EvidenceRepository.get_by_contract(contract_id)

    def export_audit_logs(self, contract_id: str) -> List[Dict[str, Any]]:
        """Export all audit log entries related to a contract."""
        return [
            vars(e) for e in AuditRepository.get_chain()
            if e.related_object_id == contract_id
        ]

    def build_case_archive(self, contract_id: str) -> Dict[str, Any]:
        """Bundle all contract data, signatures, evidence, and audit logs for legal export."""
        return {
            "contract_id": contract_id,
            "history": self.export_contract_history(contract_id),
            "versions": self.export_contract_versions(contract_id),
            "signatures": self.export_contract_signatures(contract_id),
            "evidence": self.export_contract_evidence(contract_id),
            "audit_logs": self.export_audit_logs(contract_id),
        }
