import pytest

from rsml.config import RSMLConfig
from rsml.storage import Storage


@pytest.fixture
def storage(tmp_path):
    config = RSMLConfig(
        subscriber_db=tmp_path / "subscribers.db",
        email_directory=tmp_path / "mail",
        server_secret="placeholder",
        posting_email="list@127.0.0.1",
        display_name="rsml list",
        list_id="127.0.0.1",
        archive_limit=50,
        archive_max=100,
        posting=True,
        posting_permissions="subscribers",
        precedence="list",
        fix_date=False,
    )

    return Storage(config)


@pytest.fixture
def stored_messages(storage):
    first = storage.store_message(b"msg1")
    second = storage.store_message(b"msg2")

    return [first, second]


def test_store_message(storage):
    data = b"Subject: test\r\n\r\ntest"

    path = storage.store_message(data)
    assert path.read_bytes() == data


def test_iter_messages(storage, stored_messages):
    msgs = list(storage.iter_messages("all", "all", "all"))
    assert set(msgs) == set(stored_messages)


def test_database_add_subscriber(storage):
    storage.add_subscriber("example@127.0.0.1")
    assert storage.is_subscribed("example@127.0.0.1")


def test_database_is_subscribed(storage):
    assert not storage.is_subscribed("does-not-exist@127.0.0.1")


def test_database_remove_subscriber(storage):
    storage.add_subscriber("will-be-deleted@127.0.0.1")
    storage.remove_subscriber("will-be-deleted@127.0.0.1")
    assert not storage.is_subscribed("will-be-deleted@127.0.0.1")


def test_database_iter_subscriber(storage):
    storage.add_subscriber("test1@127.0.0.1")
    storage.add_subscriber("test2@127.0.0.1")
    assert set(storage.get_subscribers()) == {"test1@127.0.0.1", "test2@127.0.0.1"}
