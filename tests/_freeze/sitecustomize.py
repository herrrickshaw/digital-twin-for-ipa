import socket, datetime as _dt, time as _t
def _blocked(*a, **k): raise OSError("network blocked")
socket.socket.connect = _blocked
socket.create_connection = _blocked
socket.getaddrinfo = _blocked
_FIX = _dt.datetime(2026, 11, 3, 12, 0, 0)
class _DT(_dt.datetime):
    @classmethod
    def now(cls, tz=None): return _FIX if tz is None else _FIX.replace(tzinfo=_dt.timezone.utc).astimezone(tz)
    @classmethod
    def utcnow(cls): return _FIX
    @classmethod
    def today(cls): return _FIX
class _D(_dt.date):
    @classmethod
    def today(cls): return _FIX.date()
_dt.datetime = _DT
_dt.date = _D
_t.time = lambda: _FIX.timestamp()
