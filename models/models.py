from dataclasses import dataclass
from typing import Optional


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