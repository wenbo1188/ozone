from . import app, client, prepare
from ozone.config import TestConfig
from . import (assertTrue_status, assertFalse_status, assertTrue_content, assertFalse_content, 
assertTrue_session, assertFalse_session)
import pytest
from  ozone.utils.db_util import get_db

def test_upload_photo_without_login(client):
    rv = client.get('/album/upload_photo/null', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertFalse_content(rv, "提交")
    assertTrue_content(rv, "You need login to continue")

    rv = client.get('/album/upload_photo/test', follow_redirects=True)
    assertTrue_status(rv, 200)
    assertFalse_content(rv, "提交")
    assertTrue_content(rv, "You need login to continue")