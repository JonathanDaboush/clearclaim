import uuid
from typing import Any, Dict, List, Optional
import db


class ProjectRepository:

    @staticmethod
    def insert_project(name: str, main_party_id: str, created_at: str) -> str:
        project_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO projects (id, name, main_party_id) VALUES (%s, %s, %s)",
            (project_id, name, main_party_id),
        )
        return project_id

    @staticmethod
    def delete_project(project_id: str) -> bool:
        rows = db.query("SELECT id FROM projects WHERE id = %s AND deleted_at IS NULL", (project_id,))
        if not rows:
            return False
        db.execute("UPDATE projects SET deleted_at = NOW() WHERE id = %s", (project_id,))
        return True

    @staticmethod
    def get_by_id(project_id: str) -> Optional[Dict[str, Any]]:
        rows = db.query(
            "SELECT id, name, main_party_id, created_at::text AS created_at, deleted_at::text AS deleted_at FROM projects WHERE id = %s",
            (project_id,),
        )
        return rows[0] if rows else None

    @staticmethod
    def get_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Return all active projects the user is a member of, including their role and verification status."""
        return db.query(
            """
            SELECT p.id, p.name, p.main_party_id, p.created_at::text AS created_at,
                   m.role_id,
                   u.verification_status,
                   (SELECT MAX(al.timestamp)::text
                    FROM audit_logs al
                    WHERE al.details::text LIKE '%%' || p.id || '%%'
                   ) AS last_activity
            FROM projects p
            JOIN memberships m ON m.project_id = p.id
            JOIN users u ON u.id = m.user_id
            WHERE m.user_id = %s AND m.soft_deleted = FALSE AND p.deleted_at IS NULL
            """,
            (user_id,),
        )
