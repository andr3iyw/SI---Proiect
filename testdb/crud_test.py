import pytest
from models.models import Algorithm, Framework, FileRecord
from repository.algorithm_repository import AlgorithmRepository
from repository.framework_repository import FrameworkRepository
from repository.file_repository import FileRepository


"""
Comanda rulare: python -m pytest testdb/crud_test.py -v
"""

@pytest.fixture
def alg_repo(): 
    return AlgorithmRepository()

@pytest.fixture
def fw_repo(): 
    return FrameworkRepository()

@pytest.fixture
def file_repo(): 
    return FileRepository()


def test_algorithm_crud(alg_repo):
    new_alg = Algorithm(
        id=None, 
        name="ChaCha20_Test", 
        type="SYMMETRIC", 
        mode=None, 
        description="Test algorithm", 
        default_key_size=256, 
        is_active=True
    )
    alg_id = None
    
    try:
        # Create
        alg_id = alg_repo.create(new_alg)
        assert alg_id is not None
        
        # Read
        algs = alg_repo.get_all()
        assert any(a['id'] == alg_id for a in algs)
        
        # Update
        alg_repo.update(alg_id, "ChaCha20_Upd", "Descriere modificata")
        upd_alg = alg_repo.get_by_id(alg_id)
        assert upd_alg['name'] == "ChaCha20_Upd"
        assert upd_alg['description'] == "Descriere modificata"

        # Replace
        rep_alg = Algorithm(
            id=alg_id,
            name="AES_Test_Replace",
            type="SYMMETRIC",
            mode="GCM",
            description="Algoritm inlocuit",
            default_key_size=128,
            is_active=False
        )
        alg_repo.replace(alg_id, rep_alg)
        replaced_alg = alg_repo.get_by_id(alg_id)
        assert replaced_alg['name'] == "AES_Test_Replace"
        assert replaced_alg['mode'] == "GCM"
        assert replaced_alg['is_active'] == 0

    finally:
        # Delete
        if alg_id is not None:
            alg_repo.delete(alg_id)
            after_delete = alg_repo.get_by_id(alg_id)
            assert after_delete is None


def test_framework_crud(fw_repo):
    new_fw = Framework(
        id=None,
        name="PyCryptodome_Test",
        version="3.20",
        language="Python",
        description="Test framework",
        is_active=True
    )
    fw_id = None
    
    try:
        # Create
        fw_id = fw_repo.create(new_fw)
        assert fw_id is not None
        
        # Read
        fws = fw_repo.get_all()
        assert any(f['id'] == fw_id for f in fws)
        
        # Update
        fw_repo.update(fw_id, "3.21", "Updated framework")
        fws_after_upd = fw_repo.get_all()
        updated_fw = next((f for f in fws_after_upd if f['id'] == fw_id), None)
        assert updated_fw is not None
        assert updated_fw['version'] == "3.21"
        
        # Replace
        rep_fw = Framework(
            id=fw_id,
            name="BouncyCastle_Replace",
            version="1.78",
            language="Java",
            description="Framework inlocuit",
            is_active=False
        )
        fw_repo.replace(fw_id, rep_fw)
        fws_after_rep = fw_repo.get_all()
        replaced_fw = next((f for f in fws_after_rep if f['id'] == fw_id), None)
        assert replaced_fw is not None
        assert replaced_fw['name'] == "BouncyCastle_Replace"
        assert replaced_fw['language'] == "Java"
        
    finally:
        # Delete
        if fw_id is not None:
            fw_repo.delete(fw_id)
            fws_final = fw_repo.get_all()
            assert not any(f['id'] == fw_id for f in fws_final)


def test_file_crud(file_repo):
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
    file_id = None
    
    try:
        # Create
        file_id = file_repo.create(new_file)
        assert file_id is not None
        
        # Read
        files = file_repo.get_all()
        assert any(f['id'] == file_id for f in files)
        
        # Update
        file_repo.update_status(file_id, "ENCRYPTED")
        files_after_upd = file_repo.get_all()
        updated_file = next((f for f in files_after_upd if f['id'] == file_id), None)
        assert updated_file is not None
        assert updated_file['status'] == "ENCRYPTED"
        
        # Replace
        rep_file = FileRecord(
            id=file_id,
            original_name="replaced_file.txt",
            original_path="D:/replaced/test.txt",
            encrypted_path="D:/replaced/enc.txt",
            decrypted_path=None,
            file_extension="txt",
            size_bytes=2048,
            checksum="rep456",
            status="DECRYPTED"
        )
        file_repo.replace(file_id, rep_file)
        files_after_rep = file_repo.get_all()
        replaced_file = next((f for f in files_after_rep if f['id'] == file_id), None)
        assert replaced_file is not None
        assert replaced_file['original_name'] == "replaced_file.txt"
        assert replaced_file['status'] == "DECRYPTED"
        
    finally:
        # Delete
        if file_id is not None:
            file_repo.delete(file_id)
            files_final = file_repo.get_all()
            assert not any(f['id'] == file_id for f in files_final)