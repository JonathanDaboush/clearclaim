# MembershipDB for persistence mapping
class MembershipDB:
    def __init__(self, id, user_id, project_id, subgroup_id, role_id):
        """
        Persistence model for DB operations.
        Args:
            id (str): Membership ID
            user_id (str): User ID
            project_id (str): Project ID
            subgroup_id (str): Subgroup ID
            role_id (str): Role ID
        """
        self.id = id
        self.user_id = user_id
        self.project_id = project_id
        self.subgroup_id = subgroup_id
        self.role_id = role_id
