"""
Custom exceptions for Wafer Detection Agent.
Provides standardized error handling across the application.
"""


class WaferDetectionError(Exception):
    """Base exception for all wafer detection errors."""
    pass


class ModelError(WaferDetectionError):
    """Base exception for model-related errors."""
    pass


class ModelLoadError(ModelError):
    """Raised when a model fails to load."""
    
    def __init__(self, model_name: str, reason: str):
        self.model_name = model_name
        self.reason = reason
        super().__init__(f"Failed to load model '{model_name}': {reason}")


class ModelInferenceError(ModelError):
    """Raised when model inference fails."""
    
    def __init__(self, model_name: str, reason: str):
        self.model_name = model_name
        self.reason = reason
        super().__init__(f"Inference failed for model '{model_name}': {reason}")


class DataError(WaferDetectionError):
    """Base exception for data-related errors."""
    pass


class InvalidInputError(DataError):
    """Raised when input data is invalid."""
    
    def __init__(self, message: str, input_type: str = "unknown"):
        self.input_type = input_type
        super().__init__(f"Invalid {input_type} input: {message}")


class FileNotFoundError(DataError):
    """Raised when a required file is not found."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"File not found: {file_path}")


class UnsupportedFileTypeError(DataError):
    """Raised when file type is not supported."""
    
    def __init__(self, file_path: str, supported_types: list):
        self.file_path = file_path
        self.supported_types = supported_types
        super().__init__(
            f"Unsupported file type for '{file_path}'. "
            f"Supported types: {', '.join(supported_types)}"
        )


class ProcessingError(WaferDetectionError):
    """Raised when wafer processing fails."""
    
    def __init__(self, stage: str, reason: str):
        self.stage = stage
        self.reason = reason
        super().__init__(f"Processing failed at stage '{stage}': {reason}")


class DatabaseError(WaferDetectionError):
    """Base exception for database-related errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


class DatabaseQueryError(DatabaseError):
    """Raised when a database query fails."""
    
    def __init__(self, query_type: str, reason: str):
        self.query_type = query_type
        self.reason = reason
        super().__init__(f"Database query '{query_type}' failed: {reason}")


class ConfigurationError(WaferDetectionError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, config_key: str, reason: str):
        self.config_key = config_key
        self.reason = reason
        super().__init__(f"Configuration error for '{config_key}': {reason}")


class ValidationError(WaferDetectionError):
    """Raised when validation fails."""
    
    def __init__(self, reason: str, attempts: int = 0, max_attempts: int = 0):
        self.attempts = attempts
        self.max_attempts = max_attempts
        message = f"Validation failed: {reason}"
        if max_attempts > 0:
            message += f" (attempt {attempts}/{max_attempts})"
        super().__init__(message)
