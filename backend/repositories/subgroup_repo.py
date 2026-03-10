import uuid
from typing import List
from models.subgroup_model import Subgroup


class SubgroupRepository:
    _subgroups: List[Subgroup] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_subgroup(project_id: str, name: str) -> str:
        """Create a subgroup under a project. Returns the new subgroup ID."""
        subgroup_id = str(uuid.uuid4())
        SubgroupRepository._subgroups.append(Subgroup(id=subgroup_id, project_id=project_id, name=name))
        return subgroup_id

    @staticmethod
    def delete_subgroup(subgroup_id: str) -> bool:
        """Remove a subgroup record. Returns True if found."""
        for sg in SubgroupRepository._subgroups:
            if sg.id == subgroup_id:
                SubgroupRepository._subgroups.remove(sg)
                return True
        return False
