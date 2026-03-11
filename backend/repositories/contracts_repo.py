import uuid
from typing import Any, Dict, List, Optional
import db


class ContractsRepository:

    @staticmethod
    def create_contract(project_id: str, created_by: str) -> str:
        contract_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO contracts (id, project_id, created_by) VALUES (%s, %s, %s)",
            (contract_id, project_id, created_by),
        )
        return contract_id

    @staticmethod
    def update_current_version(contract_id: str, version_id: str) -> bool:
        db.execute(
            "UPDATE contracts SET current_version = %s WHERE id = %s",
            (version_id, contract_id),
        )
        return True

    @staticmethod
    def get_by_id(contract_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT id, project_id, created_by, created_at::text AS created_at, current_version FROM contracts WHERE id = %s",
            (contract_id,),
        )

    @staticmethod
    def get_by_project(project_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT id, project_id, created_by, created_at::text AS created_at, current_version FROM contracts WHERE project_id = %s ORDER BY created_at",
            (project_id,),
        )
