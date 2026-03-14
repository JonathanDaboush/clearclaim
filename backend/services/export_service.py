import io
import json
import zipfile
import hashlib
import datetime
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

    def build_case_archive_zip(self, contract_id: str) -> bytes:
        """Build a ZIP bundle containing the full legal case record for a contract.

        Structure:
            contract.json          — contract metadata and all versions
            signatures.json        — all signature records with snapshot hashes
            audit_log.json         — full tamper-evident audit chain
            evidence/              — one JSON metadata file per evidence item
            timeline.json          — audit events in chronological order
            hash_manifest.json     — SHA-256 hash of every file in the archive
            EXPORT_INFO.txt        — human-readable export summary

        The hash_manifest allows a court or third party to verify that files have
        not been altered after export.
        """
        exported_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        versions     = self.export_contract_versions(contract_id)
        signatures   = self.export_contract_signatures(contract_id)
        audit_logs   = self.export_audit_logs(contract_id)
        evidence_lst = self.export_contract_evidence(contract_id)
        history      = self.export_contract_history(contract_id)

        # Timeline: audit events sorted chronologically
        timeline = sorted(audit_logs, key=lambda e: e.get("timestamp", ""))

        files: Dict[str, bytes] = {}

        files["contract.json"] = json.dumps(
            {"exported_at": exported_at, "contract_id": contract_id, **history, "versions": versions},
            indent=2, default=str,
        ).encode()

        files["signatures.json"] = json.dumps(
            {"exported_at": exported_at, "signatures": signatures},
            indent=2, default=str,
        ).encode()

        files["audit_log.json"] = json.dumps(
            {"exported_at": exported_at, "entries": audit_logs},
            indent=2, default=str,
        ).encode()

        files["timeline.json"] = json.dumps(
            {"exported_at": exported_at, "events": timeline},
            indent=2, default=str,
        ).encode()

        for ev in evidence_lst:
            ev_id = ev.get("id", "unknown")
            files[f"evidence/{ev_id}.json"] = json.dumps(ev, indent=2, default=str).encode()

        # Hash manifest — computed last, after all other files are finalised
        manifest: Dict[str, str] = {}
        for fname, content in files.items():
            manifest[fname] = hashlib.sha256(content).hexdigest()
        files["hash_manifest.json"] = json.dumps(
            {"exported_at": exported_at, "algorithm": "sha256", "files": manifest},
            indent=2,
        ).encode()

        # Human-readable summary
        files["EXPORT_INFO.txt"] = (
            f"ClearClaim Case Export\n"
            f"======================\n"
            f"Contract ID : {contract_id}\n"
            f"Exported at : {exported_at}\n"
            f"Versions    : {len(versions)}\n"
            f"Signatures  : {len(signatures)}\n"
            f"Evidence    : {len(evidence_lst)}\n"
            f"Audit events: {len(audit_logs)}\n\n"
            f"Verify integrity by recomputing SHA-256 of each file and\n"
            f"comparing against hash_manifest.json.\n"
        ).encode()

        # Assemble ZIP in memory
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname, content in files.items():
                zf.writestr(fname, content)
        return buf.getvalue()

