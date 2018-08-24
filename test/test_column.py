from . import app, client, prepare
from ozone.config import TestConfig
from . import (assertTrue_status, assertFalse_status, assertTrue_content, assertFalse_content, 
assertTrue_session, assertFalse_session)
import pytest
from  ozone.utils.db_util import get_db

def test_show_essay_without_login(client):
    rv = client.get('/column/title/1', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    

@pytest.mark.parametrize(("url", "content", "username", "password"), (
    ('/column/title/0', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/title/1', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/title/100', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/title/0', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/column/title/1', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/column/title/100', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_show_essay_login(client, prepare, url, content, username, password):
    prepare.login(username, password)
    rv = client.get(url)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, content)


@pytest.mark.parametrize(("url", "content", "username", "password"), (
    ('/column/%23test%20title/0', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/%23test%20title/1', "test essay", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/%23test%20title/100', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/all/0', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/all/1', "test essay", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/all/100', "再翻也没有啦", TestConfig.USERNAME1, TestConfig.PASSWORD),
    ('/column/%23test%20title/0', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/column/%23test%20title/1', "test essay", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/column/%23test%20title/100', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/column/all/0', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/column/all/1', "test essay", TestConfig.USERNAME2, TestConfig.PASSWORD),
    ('/column/all/100', "再翻也没有啦", TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_show_essay_login_essay(client, prepare, url, content, username, password):
    prepare.login(username, password)
    prepare.add_essay()
    rv = client.get(url)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, content)


def test_add_essay_without_login(client, app):
    rv = client.get('/column/add', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertFalse_content(rv, "提交")
    assertTrue_content(rv, "You need login to continue")

    rv = client.post('/column/add', data={
        "title":"#test title",
        "content":"test essay"
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    with app.app_context():
        db = get_db()
        assert db.cursor().execute("select * from essay where title = ? and content = ?", 
            ["#test title", "test essay"]).fetchone() is None


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_add_essay_login(prepare, client, app, username, password):
    prepare.login(username, password)
    rv = client.get('/column/add')
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "提交")

    rv = client.post('/column/add', data={
        "title":"#test title",
        "content":"test essay"
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully add an essay")
    with app.app_context():
        db = get_db()
        assert db.cursor().execute('select * from essay where title = ? and content = ?', 
            ["#test title", "test essay"]).fetchone() is not None

@pytest.mark.parametrize(("url", "status_code", "content"), (
    ("/column/update/1", 200, "You need login to continue"),
    ("/column/update", 404, "")
))
def test_update_essay_without_login(client, url, status_code, content):
    rv = client.get(url, follow_redirects=True)
    assertTrue_status(rv, status_code)
    assertTrue_content(rv, content)


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_update_essay_login(client, prepare, app, username, password):
    prepare.login(username, password)
    prepare.add_essay(num=1, title = "#test title old", content="test essay old")

    with app.app_context():
        db = get_db()
        res = db.cursor().execute("select timestamp from essay where title = ? and content = ?", 
            ["#test title old", "test essay old"]).fetchone()
        assert res is not None
    rv = client.get('/column/update', follow_redirects=True)
    assertTrue_status(rv, 404)

    rv = client.get('/column/update/1', follow_redirects=True)
    assertTrue_status(rv, 404)

    rv = client.get('/column/update/{}'.format(res["timestamp"]), follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "#test title old")
    assertTrue_content(rv, "test essay old")

    rv = client.post('/column/update/{}'.format(res["timestamp"]), data={
        "title":"#test title new",
        "content":"test essay new"
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully update an essay")
    assertTrue_content(rv, "#test title new")
    assertTrue_content(rv, "test essay new")

@pytest.mark.parametrize(("url", "status_code", "content"), (
    ("/column/delete", 404, ""),
    ("/column/delete/1", 200, "You need login to continue")
))
def test_delete_essay_without_login(client, url, status_code, content):
    rv = client.get(url, follow_redirects=True)
    assertTrue_status(rv, status_code)
    assertTrue_content(rv, content)


@pytest.mark.parametrize(("username", "password"), (
    (TestConfig.USERNAME1, TestConfig.PASSWORD),
    (TestConfig.USERNAME2, TestConfig.PASSWORD)
))
def test_delete_essay_login(client, prepare, app, username, password):
    prepare.login(username, password)
    prepare.add_essay()

    with app.app_context():
        db = get_db()
        res = db.cursor().execute("select timestamp from essay where title = ? and content = ?", 
            ["#test title", "test essay"]).fetchone()
        assert res is not None

    rv = client.get('/column/delete')
    assertTrue_status(rv, 404)
    
    rv = client.get('/column/delete/1')
    assertTrue_status(rv, 404)

    rv = client.get('/column/delete/{}'.format(res["timestamp"]), follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully delete an essay")
    assertFalse_content(rv, "#test title")
    assertFalse_content(rv, "test essay")

