from . import app, client, prepare
from ozone.config import TestConfig
from . import (assertTrue_status, assertFalse_status, assertTrue_content, assertFalse_content, 
assertTrue_session, assertFalse_session)
import pytest
from  ozone.utils.db_util import get_db

def test_show_message_without_login(client):
    rv = client.get('/message/1', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    

@pytest.mark.parametrize(("url", "content", "username", "password"), (
    ('/message/0', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/message/1', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/message/100', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/message/0', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/message/1', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/message/100', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_show_message_login(client, prepare, url, content, username, password):
    prepare.login(username, password)
    rv = client.get(url)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, content)


@pytest.mark.parametrize(("url", "content", "username", "password"), (
    ('/message/0', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/message/1', "test message", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/message/100', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/message/0', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/message/1', "test message", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/message/100', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_show_message_login_message(client, prepare, url, content, username, password):
    prepare.login(username, password)
    prepare.add_message(5, repeat=False)
    rv = client.get(url)
    assertTrue_status(rv, 200)
    if content == "test message":
        for i in range(5):
            assertTrue_content(rv, "{}_{}".format(content, i))
    else:
        assertTrue_content(rv, content)


def test_add_message_without_login(client, app):
    rv = client.get('/message/add', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertFalse_content(rv, "提交")
    assertTrue_content(rv, "You need login to continue")

    rv = client.post('/message/add', data={
        "content":"test message"
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    with app.app_context():
        db = get_db()
        assert db.cursor().execute("select * from message where content = ?", 
            ["test message",]).fetchone() is None


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_add_message_login(prepare, client, app, username, password):
    prepare.login(username, password)
    rv = client.get('/message/add')
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "提交")

    rv = client.post('/message/add', data={
        "content":"test message"
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully leave a message")
    with app.app_context():
        db = get_db()
        assert db.cursor().execute('select * from message where content = ?', 
            ["test message",]).fetchone() is not None

@pytest.mark.parametrize(("url", "status_code", "content"), (
    ("/message/update/1", 200, "You need login to continue"),
    ("/message/update", 404, "")
))
def test_update_message_without_login(client, url, status_code, content):
    rv = client.get(url, follow_redirects=True)
    assertTrue_status(rv, status_code)
    assertTrue_content(rv, content)


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_update_message_login(client, prepare, app, username, password):
    prepare.login(username, password)
    prepare.add_message(num=1, content="test message old")

    with app.app_context():
        db = get_db()
        res = db.cursor().execute("select timestamp from message where content = ?", 
            ["test message old",]).fetchone()
        assert res is not None
    rv = client.get('/message/update', follow_redirects=True)
    assertTrue_status(rv, 404)

    rv = client.get('/message/update/1', follow_redirects=True)
    assertTrue_status(rv, 404)

    rv = client.get('/message/update/{}'.format(res["timestamp"]), follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "test message old")

    rv = client.post('/message/update/{}'.format(res["timestamp"]), data={
        "content":"test message new"
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully udpate a message")
    assertTrue_content(rv, "test message new")

@pytest.mark.parametrize(("url", "status_code", "content"), (
    ("/message/delete", 404, ""),
    ("/message/delete/1", 200, "You need login to continue")
))
def test_delete_message_without_login(client, url, status_code, content):
    rv = client.get(url, follow_redirects=True)
    assertTrue_status(rv, status_code)
    assertTrue_content(rv, content)


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_delete_message_login(client, prepare, app, username, password):
    prepare.login(username, password)
    prepare.add_message()

    with app.app_context():
        db = get_db()
        res = db.cursor().execute("select timestamp from message where content = ?", 
            ["test message",]).fetchone()
        assert res is not None

    rv = client.get('/message/delete')
    assertTrue_status(rv, 404)
    
    rv = client.get('/message/delete/1')
    assertTrue_status(rv, 404)

    rv = client.get('/message/delete/{}'.format(res["timestamp"]), follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully delete a message")
    assertFalse_content(rv, "test message")

