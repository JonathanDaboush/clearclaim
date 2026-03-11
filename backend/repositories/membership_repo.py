import uuid
from typing import Any, Dict, List
import db
from models.membership_model import Membership


class MembershipRepository:

    @staticmethod
    def _to_obj(row: Dict[str, Any]) -> Membership:
        return Membership(
            id=row["id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            subgroup_id=row["subgroup_id"],
            role_id=row["role_id"],
            left_at=row.get("left_at"),
            soft_deleted=bool(row.get("soft_deleted", False)),
        )

    @staticmethod
    def insert_membership(user_id: str, project_id: str, subgroup_id: str, role_id: str) -> str:
        membership_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO memberships (id, user_id, project_id, subgroup_id, role_id) VALUES (%s, %s, %s, %s, %s)",
            (membership_id, user_id, project_id, subgroup_id, role_id),
        )
        return membership_id

    @staticmethod
    def soft_delete_membership(membership_id: str) -> bool:
        rows = db.query("SELECT id FROM memberships WHERE id = %s AND soft_deleted = FALSE", (membership_id,))
        if not rows:
            return False
        db.execute(
            "UPDATE memberships SET soft_deleted = TRUE, left_at = NOW() WHERE id = %s",
            (membership_id,),
        )
        return True

    @staticmethod
    def delete_membership(membership_id: str) -> bool:
        rows = db.query("SELECT id FROM memberships WHERE id = %s", (membership_id,))
        if not rows:
            return False
        db.execute("DELETE FROM memberships WHERE id = %s", (membership_id,))
        return True

    @staticmethod
    def get_by_project(project_id: str) -> List[Membership]:
        rows = db.query(
            "SELECT id, user_id, project_id, subgroup_id, role_id, soft_deleted, left_at::text AS left_at FROM memberships WHERE project_id = %s AND soft_deleted = FALSE",
            (project_id,),
        )
        return [MembershipRepository._to_obj(r) for r in rows]

    @staticmethod
    def get_all_by_project(project_id: str) -> List[Membership]:
        rows = db.query(
            "SELECT id, user_id, project_id, subgroup_id, role_id, soft_deleted, left_at::text AS left_at FROM memberships WHERE project_id = %s",
            (project_id,),
        )
        return [MembershipRepository._to_obj(r) for r in rows]

    @staticmethod
    def get_by_user(user_id: str) -> List[Membership]:
        rows = db.query(
            "SELECT id, user_id, project_id, subgroup_id, role_id, soft_deleted, left_at::text AS left_at FROM memberships WHERE user_id = %s AND soft_deleted = FALSE",
            (user_id,),
        )
        return [MembershipRepository._to_obj(r) for r in rows]
