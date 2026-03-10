# DevicesRepository for PostgreSQL
class DevicesRepository:
    @staticmethod
    def add_device(user_id: str, device_info: str):
        """
        Add device for user.
        Args:
            user_id (str): User ID
            device_info (str): Device info
        Returns:
            str: Device ID
        """
        pass

    @staticmethod
    def revoke_device(device_id: str):
        """
        Revoke device.
        Args:
            device_id (str): Device ID
        Returns:
            bool: Success
        """
        pass

    @staticmethod
    def is_trusted(device_id: str) -> bool:
        """
        Check if device is trusted.
        Args:
            device_id (str): Device ID
        Returns:
            bool: Trusted
        """
        pass
