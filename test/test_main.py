import pytest

from ozone.config import TestConfig
from . import (assertTrue_status, assertTrue_content, assertFalse_content,
               assertTrue_session, assertFalse_session)
from . import app, client, prepare


def test_index_visit_without_login(client):
    rv = client.get('/')
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "Ozone")
    assertTrue_content(rv, "登录")


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD),
))
def test_login_correct(client, username, password):
    rv = client.get('/login')
    assertTrue_status(rv, 200)
    
    # Login with correct username and password
    rv = client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)
    assertTrue_status(rv, 200)

    assertTrue_content(rv, "You have successfully logged in")
    assertTrue_content(rv, "喜欢的音乐")
    assertTrue_content(rv, "精选专栏")

    with client:
        client.get('/')
        assertTrue_session("logged_in")
        assertTrue_session("logged_user", username)


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1 + 'x', TestConfig.PASSWORD),
    (TestConfig.USERNAME1, TestConfig.PASSWORD + 'x'),
))
def test_login_incorrect(client, username, password):
    # Login with incorrect username or password
    rv = client.post('/login', data={
        'username': username,
        'password': password
    })
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "Wrong username or password")

    with client:
        client.get('/')
        assertFalse_session("logged_in")
        assertFalse_session("logged_user")


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD),
))
def test_logout(client, username, password):
    # Logout without login first
    rv = client.get('/logout', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have not logged in yet")

    # Login first
    rv = client.post('/login', data={
        'username': username,
        'password': password
    })
    rv = client.get('/logout', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully logged out")

    with client:
        client.get('/')
        assertFalse_session("logged_in")
        assertFalse_session("logged_user")


def test_manage_message_without_login(client):
    # Visit without login
    rv = client.get('/manage/message', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    assertFalse_content(rv, "操作")


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD),
))
def test_manage_message_login(client, prepare, username, password):
    # Visit with login
    prepare.login(username, password)
    prepare.add_message()
    rv = client.get('/manage/message')
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "操作")
    assertTrue_content(rv, "test message")


def test_manage_column_without_login(client):
    # Visit without login
    rv = client.get('/manage/column', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    assertFalse_content(rv, "操作")


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD),
))
def test_manage_column_login(client, prepare, username, password):
    # Visit with login
    prepare.login(username, password)
    prepare.add_essay()
    rv = client.get('/manage/column')
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "操作")
    assertTrue_content(rv, "#test title")
    assertTrue_content(rv, "test essay")


def test_manage_album_without_login(client):
    # Visit without login
    rv = client.get('/manage/album', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    assertFalse_content(rv, "操作")


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD),
))
def test_manage_album_login(client, prepare, username, password):
    # Visit with login
    prepare.login(username, password)
    rv = client.get('/manage/album')
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "操作")
