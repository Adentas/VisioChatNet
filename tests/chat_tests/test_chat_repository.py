import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.repository.chat_repository import *
from unittest.mock import mock


def test_start_chat_success(mock_db_session, mock_cache):
    user_id = 123
    result = start_chat(mock_db_session, user_id)

    assert result is not None
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    mock_cache.delete.assert_called_with(f"user_chats_{user_id}")


def test_send_message_success_text(mock_db_session, mock_cache):
    chat_id, user_id = 1, 123
    result = send_message(mock_db_session, chat_id, user_id, "user", "Hello, world!")

    assert result is not None
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    mock_cache.delete.assert_has_calls(
        [mock.call(f"chat_history_{chat_id}"), mock.call(f"user_chats_{user_id}")]
    )


def test_get_user_chats_success(mock_db_session, mock_cache):
    user_id = 123
    result = get_user_chats(mock_db_session, user_id)

    assert result is not None
    mock_db_session.query.assert_called()
    mock_cache.get.assert_called_with(f"user_chats_{user_id}")


def test_get_chat_history_success(mock_db_session, mock_cache):
    chat_id = 1
    result = get_chat_history(mock_db_session, chat_id)

    assert result is not None
    mock_db_session.query.assert_called()
    mock_cache.get.assert_called_with(f"chat_history_{chat_id}")


def test_delete_chat_success(mock_db_session, mock_cache):
    chat_id = 1
    result = delete_chat(mock_db_session, chat_id)

    assert result is True
    mock_db_session.delete.assert_called()
    mock_db_session.commit.assert_called()
    mock_cache.delete.assert_called_with(f"chat_history_{chat_id}")


def test_rename_chat_success(mock_db_session, mock_cache):
    chat_id = 1
    new_title = "New Title"
    result = rename_chat(mock_db_session, chat_id, new_title)

    assert result is True
    mock_db_session.commit.assert_called()
