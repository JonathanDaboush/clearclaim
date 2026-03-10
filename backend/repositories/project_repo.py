import uuid
import datetime
from typing import List
from models.project_model import Project


class ProjectRepository:
    _projects: List[Project] = []  # In-memory (replace with DB in production)

    @staticmethod
    def insert_project(name: str, main_party_id: str, created_at: str) -> str:
        """Create a new project record. Returns the new project ID."""
        project_id = str(uuid.uuid4())
        ProjectRepository._projects.append(Project(
            id=project_id,
            name=name,
            main_party_id=main_party_id,
            created_at=created_at,
            deleted_at=None,
        ))
        return project_id

    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Soft-delete a project by setting deleted_at. Returns True if found."""
        for project in ProjectRepository._projects:
            if project.id == project_id and project.deleted_at is None:
                project.deleted_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return True
        return False
