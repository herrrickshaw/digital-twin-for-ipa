"""Characterisation of build_layer45_media_rss_sweep.main with stub rosters, feeds and article pages."""
import build_layer45_media_rss_sweep as l45
from conftest import sha

GOLDEN = {"out": "469b18c008db7d593d76e2c120b917530e8211e3b2abf8181b35730c4cbc8915", "json": "e20b5b3ede1b9700a9371f931598fd549fd328e88e3f6e780c5aeb94d176fc3b", "doc": "f73b3b755b758e6923d42f6b81d1188a1d43652d804873761567c87c80be7c8a", "archive": "40c57b93ede49b9202c42d9299da9195c390a32c78010deddaf999e8f1dda395"}

FEED_XML = """<rss><channel>
<item><title><![CDATA[Toyota Motor to invest Rs 5,000 crore in new plant]]></title><description>expansion plans</description><link>http://news/a1</link><pubDate>Mon, 02 Nov 2026</pubDate></item>
<item><title>Weather update for Mumbai</title><description>rain</description><link>http://news/a2</link><pubDate>Mon, 02 Nov 2026</pubDate></item>
<item><title>Siemens Energy joint venture announced</title><description>d</description><link>http://news/a3</link><pubDate>Tue, 03 Nov 2026</pubDate></item>
<item><title>Toyota Motor to invest Rs 5,000 crore in new plant</title><description>dup</description><link>http://news/a1</link><pubDate>Mon, 02 Nov 2026</pubDate></item>
</channel></rss>"""


def _fake_curl(url, timeout=20):
    if url.startswith("http://feed/ok"):
        return "200", FEED_XML
    if url.startswith("http://feed/bad"):
        return "503", ""
    if url == "http://news/a1":
        return "200", '{"articleBody": "Toyota will build a plant.", "x": 1}'
    return "ERR", "boom"


def test_main_outputs_identical(tmp_path, monkeypatch, capsys, frozen_today):
    (tmp_path / "state").mkdir()
    monkeypatch.setattr(l45, "OUT_JSON", str(tmp_path / "layers" / "45.json"))
    monkeypatch.setattr(l45, "OUT_DOC", str(tmp_path / "45.md"))
    monkeypatch.setattr(l45, "ARCHIVE", str(tmp_path / "state" / "news_articles.jsonl"))
    monkeypatch.setattr(l45, "FEEDS", {"SRC1": {"auto": "http://feed/ok1", "bad": "http://feed/bad"}, "SRC2": {"auto": "http://feed/ok2"}})
    monkeypatch.setattr(l45, "sh_curl", _fake_curl)
    monkeypatch.setattr(l45, "load_all_rosters", lambda: {"JP": [{"name": "Toyota Motor Corp", "ticker": "7203.T", "exchange": "TSE", "country": "JP"},
                                                                  {"name": "Launch Two Acquisition Corp", "ticker": "LTAC", "exchange": "NQ", "country": "US"}],
                                                          "DE": [{"name": "Siemens Energy AG", "ticker": "ENR.DE", "exchange": "XETRA", "country": "DE"}]})
    monkeypatch.setattr(l45, "known_names", lambda: {"siemens energy ag"})
    l45.main()
    out = capsys.readouterr().out.replace(str(tmp_path), "<TMP>")
    got = {"out": sha(out), "json": sha((tmp_path / "layers" / "45.json").read_bytes()),
           "doc": sha((tmp_path / "45.md").read_bytes()), "archive": sha((tmp_path / "state" / "news_articles.jsonl").read_bytes())}
    assert "Toyota Motor Corp" in out and "ERROR 503" in out  # the scenario really exercises matches and feed errors
    assert got == GOLDEN
