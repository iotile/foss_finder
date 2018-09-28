class CheckError(Exception):
    """
    Base class for exceptions raised by checks.
    """
    pass


class Check():
    """
    The aim of this class is to check that the information of a given dependency is correct.
    It should raise an exception if it isn't.
    Derived classes must implement:
    - NAME attribute
    - DESCRIPTION attribute
    - check method
    """

    def __repr__(self):
        return f'<{self.NAME} - {self.DESCRIPTION}>'

    def check(self, package_info):
        """
        Abstract method: derived classes should implement it.
        Should raise an exception if check doesn't pass.
        """
        raise NotImplementedError
