"""HTTP, translation and language helpers shared by the state fetchers."""
import json, ssl, sys, time, urllib.error, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"


def _get(url, timeout=45, opener=None, data=None, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs)
    op = opener.open if opener else urllib.request.urlopen
    try:
        with op(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.URLError as e:
        # several Indian govt sites serve incomplete cert chains that curl's CA
        # bundle tolerates but Python rejects -- retry unverified (public,
        # read-only data; no credentials ever sent on these requests)
        if isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError):
            print(f"warning: broken cert chain, retrying unverified: {url.split('/')[2]}", file=sys.stderr)
            if opener:
                raise  # cookie-carrying openers keep strict TLS
            ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read().decode("utf-8", "replace")
        # some sites (e.g. telangana.gov.in) intermittently fail the TLS
        # handshake itself against Python's default fingerprint -- not a cert
        # problem, urllib has no retry path for it. Confirmed 2026-08-24: 15/15
        # cron runs failed this way for TS while a Scrapling (curl_cffi,
        # real-browser TLS fingerprint) request to the same URL succeeded
        # immediately. Fall back to it for plain GETs only -- cookie/opener
        # flows keep their own session handling, scrapling doesn't replicate it.
        if opener or data:
            raise
        try:
            from scrapling.fetchers import Fetcher
        except ImportError:
            raise
        print(f"warning: urllib failed ({e}), retrying via scrapling: {url.split('/')[2]}", file=sys.stderr)
        resp = Fetcher.get(url, timeout=timeout, headers=hdrs)
        return resp.body.decode("utf-8", "replace")


def _get_json(url, **kw):
    return json.loads(_get(url, **kw))


# ---------------------------------------------------------------- translation
_TRANSLATE_FAILS = 0


def translate_en(text):
    """Best-effort machine translation to English via the free gtx endpoint.
    Returns None on failure or when disabled; trips a breaker after 5 failures."""
    global _TRANSLATE_FAILS
    if _TRANSLATE_FAILS >= 5 or not text:
        return None
    try:
        url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
            {"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": text[:900]})
        d = _get_json(url, timeout=20)
        out = "".join(seg[0] for seg in d[0] if seg and seg[0]).strip()
        time.sleep(0.3)
        return out or None
    except Exception:
        _TRANSLATE_FAILS += 1
        return None


def _is_english(s):
    return all(ord(c) < 0x530 for c in s or "")


# ---------------------------------------------------------------- MP (daily)
def _decode_mp_newsid(raw):
    """mpinfo obfuscates newsid by adding 0x80 to each ASCII char."""
    try:
        return "".join(chr(ord(c) - 0x80) if ord(c) >= 0x80 else c for c in raw or "")
    except Exception:
        return raw or ""
