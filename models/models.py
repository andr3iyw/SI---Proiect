from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Algorithm:
    id: Optional[int]
    name: str
    type: str
    mode: Optional[str]
    description: Optional[str]
    default_key_size: Optional[int]
    is_active: bool = True


@dataclass
class Framework:
    id: Optional[int]
    name: str
    version: Optional[str]
    language: Optional[str]
    description: Optional[str]
    is_active: bool = True


@dataclass
class FileRecord:
    id: Optional[int]
    original_name: str
    original_path: str
    encrypted_path: Optional[str]
    decrypted_path: Optional[str]
    file_extension: Optional[str]
    size_bytes: int
    checksum: Optional[str]
    status: str = "UPLOADED"


@dataclass
class KeyStorage:
    id: Optional[int]
    name: str
    algorithm_id: int
    key_type: str
    key_size: int
    key_path: Optional[str]
    key_value_encrypted: Optional[str]
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

@dataclass
class CryptoOperation:
    id: Optional[int]
    file_id: int
    algorithm_id: int
    key_id: int
    framework_id: int
    operation_type: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    