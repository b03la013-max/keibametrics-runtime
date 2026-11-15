import datetime as dt, sys
sys.path.insert(0, "runtime")
import jra_owner_issue_delivery as d

POST = "2026-11-21T10:05:00+09:00"


def test_compose_final_and_no_bet():
    b = d.compose("KM-JRA-TKY-20261121-R01", POST, "馬単\n1着\n└─ 5\n")
    assert b.startswith("**【東京1R】** 11/21 発走 10:05") and "└─ 5" in b
    assert "見送り" in d.compose("KM-JRA-KYO-20261121-R02", POST, None, "AKI_SINGLE_HEAD_FORBIDDEN")


def test_never_posts_after_post_time():
    called = []
    at = dt.datetime.fromisoformat(POST)
    r = d.deliver("KM-JRA-TKY-20261121-R01", POST, "x", now=at, post=lambda i, b: called.append(1))
    assert r["status"] == "SKIPPED_POST_TIME_PASSED" and not called
    r = d.deliver("KM-JRA-TKY-20261121-R01", POST, "x", now=at - dt.timedelta(minutes=40),
                  post=lambda i, b: {"html_url": "u"})
    assert r["status"] == "DELIVERY_ACCEPTED" and r["issue"] == 421 and r["user_ack"] == "ACK_UNVERIFIED"
