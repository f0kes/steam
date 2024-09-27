from typing import TypeVar, Generic

T = TypeVar('T')


class Result(Generic[T]):
    def __init__(self, success: bool, data: T = None, message: str = None):
        self.success = success
        self.data = data
        self.message = message

    @classmethod
    def success(cls, data: T):
        return cls(success=True, data=data)

    @classmethod
    def failure(cls, message: str):
        return cls(success=False, message=message)

    def is_failure(self):
        return not self.success
