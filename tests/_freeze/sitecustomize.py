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

# glob.glob returns directory order, which is filesystem-specific (APFS vs ext4). The builders' output for
# layers/12_state_catalog depends on it (a later file overwrites an earlier one for a state listed twice),
# and the golden hashes were captured on APFS. Replay that order explicitly so the run is the same everywhere.
import glob as _g, os as _os
_ORDER = ["north_up_hr_pb_uk_hp_dl.json", "central_east_mp_cg_od_wb_jh_br.json", "ocr_extracts_gj_pb.json",
          "west_gj_mh_rj_goa.json", "ne_states_jk.json", "south_tn_ka.json", "south_tg_ap_kl.json"]
_orig_glob = _g.glob
def _stable_glob(*a, **k):
    found = _orig_glob(*a, **k)
    return sorted(found, key=lambda p: (_ORDER.index(_os.path.basename(p)) if _os.path.basename(p) in _ORDER else len(_ORDER), p))
_g.glob = _stable_glob
