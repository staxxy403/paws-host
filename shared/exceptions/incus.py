class IncusError(Exception):
    pass

class IncusOperationError(IncusError):
    def __init__(self, message: str, operation_id: str | None = None, raw_data: dict | None = None):
        super().__init__(message)
        self.operation_id = operation_id
        self.raw_data = raw_data

class IncusNodeUnreachableError(IncusError):
    pass
