# Declare singleton base class
class SingletonBase:
    # Private variables
    _instance = None
    # Reference method to get singleton base instance
    @classmethod
    def get_instance(cls, *args, **kwargs):
        # Check for instance
        if cls._instance is None:
            # Create instance from class with given args
            cls._instance = cls(*args, **kwargs)
            # Indicate instance initialized
            print(f"Initialized singleton {cls.__name__}")
        return cls._instance