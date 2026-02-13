from apps.serial_error import make_serial_error
from apps.serial_error_store import ErrorStore


def _mk(i: int):
    return make_serial_error(
        layer="serial",
        kind="timeout",
        op=f"op{i}",
        retryable=True,
        detail=str(i),
    )


def test_get_last_empty_is_none():
    s = ErrorStore()
    assert s.get_last() is None


def test_record_and_get_last():
    s = ErrorStore()
    s.record(_mk(1))
    last = s.get_last()
    assert last is not None
    assert last["op"] == "op1"


def test_get_recent_newest_first():
    s = ErrorStore()
    s.record(_mk(1))
    s.record(_mk(2))
    s.record(_mk(3))
    rec = s.get_recent(limit=2)
    assert [e["op"] for e in rec] == ["op3", "op2"]


def test_ring_buffer_max_20():
    s = ErrorStore()
    for i in range(25):
        s.record(_mk(i))
    rec = s.get_recent(limit=100)
    assert len(rec) == 20
    # newest should be last inserted
    assert rec[0]["op"] == "op24"
    # oldest retained should be op5 (since 0..4 dropped)
    assert rec[-1]["op"] == "op5"


def test_get_recent_limit_zero():
    s = ErrorStore()
    s.record(_mk(1))
    assert s.get_recent(limit=0) == []
