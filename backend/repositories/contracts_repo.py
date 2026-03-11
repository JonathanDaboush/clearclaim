import uuid
from typing import Any, Dict, List, Optional
import db


class ContractsRepository:

    @staticmethod
    def create_contract(project_id: str, created_by: str, name: str = 'Untitled Contract') -> str:
        contract_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO contracts (id, project_id, created_by, name) VALUES (%s, %s, %s, %s)",
            (contract_id, project_id, created_by, name),
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
            """
            SELECT c.id, c.project_id, c.name, c.created_by,
                   c.created_at::text AS created_at,
                   c.current_version, c.status,
                   MAX(cv.created_at)::text AS last_revised_at
            FROM contracts c
            LEFT JOIN contract_versions cv ON cv.contract_id = c.id
            WHERE c.id = %s
            GROUP BY c.id, c.project_id, c.name, c.created_by, c.created_at, c.current_version, c.status
            """,
            (contract_id,),
        )

    @staticmethod
    def get_by_project(project_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT c.id, c.project_id, c.name, c.created_by,
                   c.created_at::text AS created_at,
                   c.current_version, c.status,
                   MAX(cv.created_at)::text AS last_revised_at
            FROM contracts c
            LEFT JOIN contract_versions cv ON cv.contract_id = c.id
            WHERE c.project_id = %s
            GROUP BY c.id, c.project_id, c.name, c.created_by, c.created_at, c.current_version, c.status
            ORDER BY c.created_at
            """,
            (project_id,),
        )
