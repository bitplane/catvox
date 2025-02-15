class Data:
    """
    A block of data passing through the pipeline
    """

    def __init__(self, data, metadata=None):
        self.data = data
        self.metadata = metadata or {}

    def match(self, pattern: dict, subtree=None) -> bool:
        """
        Check if the metadata matches the pattern
        """
        if subtree is None:
            subtree = self.metadata

        for key, value in pattern.items():
            if key not in subtree:
                return False
            elif isinstance(value, dict):
                if not self.match(value, subtree[key]):
                    return False
            elif isinstance(value, list):
                actual_set = set(subtree[key])
                desired_set = set(value)
                if not desired_set.issubset(actual_set):
                    return False
            elif subtree[key] != value:
                return False

        return True
