from models import Algorithm, Framework, FileRecord
from algorithm_repository import AlgorithmRepository
from framework_repository import FrameworkRepository
from file_repository import FileRepository


def test_algorithm_crud():
    repo = AlgorithmRepository()

    print("\n--- TEST ALGORITHM CRUD ---")

    new_algorithm = Algorithm(
        id=None,
        name="ChaCha20",
        type="SYMMETRIC",
        mode=None,
        description="Test algorithm",
        default_key_size=256,
        is_active=True
    )

    algorithm_id = repo.create(new_algorithm)
    print(f"Inserted algorithm id: {algorithm_id}")

    all_algorithms = repo.get_all()
    print("All algorithms:", all_algorithms)

    repo.update(algorithm_id, "ChaCha20-Updated", "Updated description")
    updated_algorithm = repo.get_by_id(algorithm_id)
    print("Updated algorithm:", updated_algorithm)

    repo.delete(algorithm_id)
    print(f"Deleted algorithm id: {algorithm_id}")


def test_framework_crud():
    repo = FrameworkRepository()

    print("\n--- TEST FRAMEWORK CRUD ---")

    new_framework = Framework(
        id=None,
        name="PyCryptodome",
        version="3.20",
        language="Python",
        description="Test framework",
        is_active=True
    )

    framework_id = repo.create(new_framework)
    print(f"Inserted framework id: {framework_id}")

    all_frameworks = repo.get_all()
    print("All frameworks:", all_frameworks)

    repo.update(framework_id, "3.21", "Updated framework")
    updated_frameworks = repo.get_all()
    print("Frameworks after update:", updated_frameworks)

    repo.delete(framework_id)
    print(f"Deleted framework id: {framework_id}")


def test_file_crud():
    repo = FileRepository()

    print("\n--- TEST FILE CRUD ---")

    new_file = FileRecord(
        id=None,
        original_name="test_file.txt",
        original_path="C:/test/test_file.txt",
        encrypted_path=None,
        decrypted_path=None,
        file_extension="txt",
        size_bytes=1024,
        checksum="test123",
        status="UPLOADED"
    )

    file_id = repo.create(new_file)
    print(f"Inserted file id: {file_id}")

    all_files = repo.get_all()
    print("All files:", all_files)

    repo.update_status(file_id, "ENCRYPTED")
    updated_files = repo.get_all()
    print("Files after update:", updated_files)

    repo.delete(file_id)
    print(f"Deleted file id: {file_id}")


if __name__ == "__main__":
    test_algorithm_crud()
    test_framework_crud()
    test_file_crud()
    print("\nAll CRUD tests finished.")