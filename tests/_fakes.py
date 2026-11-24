"""Small offline fakes shared by the second-round script tests."""
import json
import subprocess


class FakeResp:
    """Duck-types urllib responses *and* requests.Response."""

    def __init__(self, body=b"", status=200, headers=None, jsonobj=None):
        if jsonobj is not None:
            body = json.dumps(jsonobj).encode()
        if isinstance(body, str):
            body = body.encode()
        self._body = body
        self.status_code = status
        self.status = status
        self.headers = headers or {}
        self.ok = status < 400

    @property
    def content(self):
        return self._body

    @property
    def text(self):
        return self._body.decode("utf-8", "replace")

    def read(self, *a):
        return self._body

    def json(self):
        return json.loads(self._body)

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"{self.status_code}")

    def getcode(self):
        return self.status_code

    def info(self):
        return self.headers

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def completed(stdout=b"", returncode=0, stderr=b""):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path
