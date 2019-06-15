import pytest
from ozone.config import TestConfig
from ozone import my_truncate
from ozone.utils.reminder_util import EmailReminder


def test_my_truncate():
    test_case_normal = ['x' * 10, 'y' * 255]
    test_case_long = ['z' * 300]
    result = my_truncate(test_case_normal[0])
    assert (result == test_case_normal[0])

    result = my_truncate(test_case_normal[1])
    assert (result == test_case_normal[1])

    result = my_truncate(test_case_long[0])
    assert (result == 'z' * 255 + '...')


def test_email_reminder():
    mail_server = TestConfig.MAIL_SERVER
    mail_port = TestConfig.MAIL_PORT
    mail_username = TestConfig.MAIL_USERNAME
    mail_password = TestConfig.MAIL_PASSWORD
    debug_mode = True if TestConfig.DEBUG else False
    logger = None

    email_reminder = EmailReminder(mail_server, mail_port, mail_username, mail_password, debug_mode=debug_mode,
                                   logger=logger)
    msg = 'test_message'
    receiver = TestConfig.USER1_MAILADDRESS
    receiver_name = TestConfig.USERNAME1_CN
    res = email_reminder.send(receiver, receiver_name, msg)
    assert (res == True)
