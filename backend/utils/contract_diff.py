import difflib


class ContractDiff:
    @staticmethod
    def diff_versions(version_a: str, version_b: str) -> str:
        """Return a unified diff string between two contract version text strings."""
        diff = difflib.unified_diff(
            version_a.splitlines(keepends=True),
            version_b.splitlines(keepends=True),
            fromfile="version_a",
            tofile="version_b",
        )
        return "".join(diff)
