import os
import shutil
import pytest
from moonball_archiver import MoonBallArchive

def setup_module(module):
    module.test_dir = "test_data"
    module.test_file_path = os.path.join(test_dir, "test_file.txt")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    with open(test_file_path, 'w') as f:
        f.write("This is a test file.")

def teardown_module(module):
    shutil.rmtree(test_dir)

def test_placeholder():
    assert True

def test_archive_creation():
    archive = MoonBallArchive()
    archive.add_file(test_file_path)
    assert len(archive.files) > 0, "Failed to add file to archive."

def test_empty_archive():
    archive = MoonBallArchive()
    assert len(archive.files) == 0, "Archive should be empty."

def test_add_directory():
    archive_dir = os.path.join(test_dir, "test_subdir")
    sub_test_file_path = os.path.join(archive_dir, "sub_test_file.txt")

    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    with open(sub_test_file_path, 'w') as f:
        f.write("This is a test file in a directory.")

    archive = MoonBallArchive()
    archive.add_directory(test_dir)
    
    assert len(archive.files) == 2, "Failed to add all files from directory."

def test_save_archive():
    archive = MoonBallArchive()
    archive.add_file(test_file_path)
    output_path = os.path.join(test_dir, "test_archive.mnbl")
    archive.save(output_path)

    assert os.path.exists(output_path), f"Archive not saved at {output_path}"

def test_extract_archive():
    input_archive_path = os.path.join(test_dir, "test_archive.mnbl")
    output_dir = os.path.join(test_dir, "extracted_files")

    if not os.path.exists(input_archive_path):
        archive = MoonBallArchive()
        archive.add_file(test_file_path)
        archive.save(input_archive_path)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    archive = MoonBallArchive()
    archive.extract(input_archive_path, output_dir)

    extracted_file_path = os.path.join(output_dir, "test_file.txt")
    assert os.path.exists(extracted_file_path), f"File not extracted at {extracted_file_path}"

def test_semantic_search():
    archive = MoonBallArchive()
    archive.add_file(test_file_path)
    
    query = "This is a test file."
    results = archive.semantic_search(query)

    assert len(results) > 0, "Semantic search failed to find any matching files."

if __name__ == "__main__":
    pytest.main([__file__])