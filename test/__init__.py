import pytest
import os
import tempfile
from ozone.config import TestConfig
from ozone import create_app

@pytest.fixture
def client():
    # Prepare path for testing
    db_fd, TestConfig.DATABASE = tempfile.mkstemp(suffix=".db")
    # print("database path: {}".format(TestConfig.DATABASE))
    common_path = tempfile.mkdtemp()
    # print("common_path: {}".format(common_path))
    TestConfig.PLAYLIST_PATH = common_path
    TestConfig.SONGS_PATH = common_path
    TestConfig.UPLOADED_PHOTOS_DEST = common_path

    app = create_app(TestConfig)
    client = app.test_client()
    
    yield client

    os.close(db_fd)
    os.unlink(TestConfig.DATABASE)
    os.system("rm -rf {}".format(common_path))

def assertTrue_status(response, status_code):
    assert response.status_code == status_code

def assertFalse_status(response, status_code):
    assert response.status_code != status_code

def assertTrue_content(response, content):
    assert content in response.get_data(as_text=True)

def assertFalse_content(response, content):
    assert content not in response.get_data(as_text=True)

def prepare_resource(func):
    def wrapper(client):
        # do resource prepare here
        func(client)
    return wrapper