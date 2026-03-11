import uuid
from typing import List
import db


class SubgroupRepository:

    @staticmethod
    def insert_subgroup(project_id: str, name: str) -> str:
        subgroup_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO subgroups (id, project_id, name) VALUES (%s, %s, %s)",
            (subgroup_id, project_id, name),
        )
        return subgroup_id

    @staticmethod
    def delete_subgroup(subgroup_id: str) -> bool:
        rows = db.query("SELECT id FROM subgroups WHERE id = %s", (subgroup_id,))
        if not rows:
            return False
        db.execute("DELETE FROM subgroups WHERE id = %s", (subgroup_id,))
        return True
