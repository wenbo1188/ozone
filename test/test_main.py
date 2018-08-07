from . import client, prepare_resource
from ozone.config import TestConfig
from . import assertTrue_status, assertFalse_status, assertTrue_content, assertFalse_content

def test_index_visit_without_login(client):
    rv = client.get('/')
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "Ozone")
    assertTrue_content(rv, "登录")

@prepare_resource
def test_login_user1_correct(client):
    rv = client.get('/login')
    assertTrue_status(rv, 200)
    
    # Login with correct username and password
    rv = client.post('/login', data={
        'username':TestConfig.USERNAME1,
        'password':TestConfig.PASSWORD
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully logged in")
    assertTrue_content(rv, "喜欢的音乐")
    assertTrue_content(rv, "精选专栏")

@prepare_resource
def test_login_user2_correct(client):
    rv = client.get('/login')
    assertTrue_status(rv, 200)
    
    # Login with correct username and password
    rv = client.post('/login', data={
        'username':TestConfig.USERNAME2,
        'password':TestConfig.PASSWORD
    }, follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully logged in")
    assertTrue_content(rv, "喜欢的音乐")
    assertTrue_content(rv, "精选专栏")

def test_login_incorrect(client):
    # Login with incorrect username or password
    rv = client.post('/login', data={
        'username':TestConfig.USERNAME1 + 'x',
        'password':TestConfig.PASSWORD
    })
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "Wrong username or password")

    rv = client.post('/login', data={
        'username':TestConfig.USERNAME1,
        'password':TestConfig.PASSWORD + 'x'
    })
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "Wrong username or password")

def test_logout(client):
    # logout without login first
    rv = client.get('/logout', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have not logged in yet")

    # login first
    rv = client.post('/login', data={
        'username':TestConfig.USERNAME1,
        'password':TestConfig.PASSWORD
    })
    rv = client.get('/logout', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You have successfully logged out")

def test_manage_message(client):
    # visit without login
    rv = client.get('/manage/message', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertTrue_content(rv, "You need login to continue")
    assertFalse_content(rv, "操作")