import pytest
import os
import tempfile
from ozone.config import TestConfig
from ozone import create_app
from flask import session

class Prepare(object):
    def __init__(self, client):
        self._client = client
    
    def login(self, username, password):
        return self._client.post('/login', data={
            'username':username,
            'password':password
        })
    
    def logout(self):
        return self._client.get('/logout')

    def add_message(self, num=1, content="test message", repeat=True):
        for i in range(num):
            if repeat:
                self._client.post('/message/add', data={
                    'content':content
                })
            else:
                self._client.post('/message/add', data={
                    'content':'{}_{}'.format(content, i)
                })
    
    def add_essay(self, num=1, title="#test title", content="test essay", repeat=True):
        for i in range(num):
            if repeat:
                self._client.post('/column/add', data={
                    'title':title,
                    'content':content
                })
            else:
                self._client.post('/column/add', data={
                    'title':'{}_{}'.format(title, i),
                    'content':'{}_{}'.format(content, i)
                })
    
    def add_photo(self):
        pass

@pytest.fixture
def app():
    # Prepare path for testing
    db_fd, TestConfig.DATABASE = tempfile.mkstemp(suffix=".db")
    common_path = tempfile.mkdtemp()
    TestConfig.PLAYLIST_PATH = common_path
    TestConfig.SONGS_PATH = common_path
    TestConfig.UPLOADED_PHOTOS_DEST = common_path

    app = create_app(TestConfig)
    
    yield app

    os.close(db_fd)
    os.unlink(TestConfig.DATABASE)
    os.removedirs(common_path)

@pytest.fixture
def client(app):
    return app.test_client()
    
@pytest.fixture
def prepare(client):
    return Prepare(client)

def assertTrue_status(response, status_code):
    assert response.status_code == status_code

def assertFalse_status(response, status_code):
    assert response.status_code != status_code

def assertTrue_content(response, content):
    assert content in response.get_data(as_text=True)

def assertFalse_content(response, content):
    assert content not in response.get_data(as_text=True)

def assertTrue_session(key, value=None):
    assert key in session
    if value:
        assert session[key] == value

def assertFalse_session(key, value=None):
    if value:
        assert key in session
        assert session[key] != value
    else:
        assert key not in session

# def prepare_login(func):
#     def wrapper(client):
#         # test for user1
#         prepare = Prepare(client)
#         prepare.login(TestConfig.USERNAME1, TestConfig.PASSWORD)
#         func(client)
#         prepare.logout()

#         # test for user2
#         prepare = Prepare(client)
#         prepare.login(TestConfig.USERNAME2, TestConfig.PASSWORD)
#         func(client)
#         prepare.logout()

#     return wrapper

# def prepare_login_withmessage(func):
#     def wrapper(client):
#         # test for user1
#         prepare = Prepare(client)
#         prepare.login(TestConfig.USERNAME1, TestConfig.PASSWORD)
#         prepare.add_message(5)
#         func(client)
#         prepare.logout()

#         # test for user2
#         prepare = Prepare(client)
#         prepare.login(TestConfig.USERNAME2, TestConfig.PASSWORD)
#         prepare.add_message(5)
#         func(client)
#         prepare.logout()

#     return wrapper

# def prepare_login_withessay(func):
#     def wrapper(client):
#         # test for user1
#         prepare = Prepare(client)
#         prepare.login(TestConfig.USERNAME1, TestConfig.PASSWORD)
#         prepare.add_essay(5)
#         func(client)
#         prepare.logout()

#         # test for user2
#         prepare = Prepare(client)
#         prepare.login(TestConfig.USERNAME2, TestConfig.PASSWORD)
#         prepare.add_essay(5)
#         func(client)
#         prepare.logout()

#     return wrapper