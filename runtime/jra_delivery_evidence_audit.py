"""Read-only JRA FINAL delivery evidence reconciliation.

Never sends notifications, rewrites signed FINAL, or infers human receipt from
a published GitHub artifact. Only reports what independent records establish.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime


def _sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _verify_record(record, name):
    if not isinstance(record, dict):
        raise ValueError(name + "_RECORD_REQUIRED")
    if record.get("sha256") != _sha({k: v for k, v in record.items() if k != "sha256"}):
        raise ValueError(name + "_HASH_MISMATCH")


def _time(value):
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_REQUIRED")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return result


def audit_delivery(*, final, publication=None, availability=None,
                   notification=None, recipient_ack=None):
    """Return separate publication, provider-send and recipient-ack states.

    Receipt references are evidence only; this does not independently verify
    FINAL's Ed25519 signature or the actual GitHub remote readback.
    """
    if not isinstance(final, dict) or not isinstance(final.get("race_id"), str):
        raise ValueError("FINAL_REQUIRED")
    race_id, final_sha = final["race_id"], final.get("sha256")
    if not isinstance(final_sha, str) or len(final_sha) != 64:
        raise ValueError("FINAL_SHA_REQUIRED")
    post = _time(final["scheduled_post_at"])
    result = {"race_id": race_id, "final_sha256": final_sha,
              "final_signature_independently_verified": False,
              "canonical_availability": "UNVERIFIED",
              "notification_sent": "UNVERIFIED",
              "recipient_acknowledged": "UNVERIFIED",
              "pre_post_delivery": "UNVERIFIED",
              "actual_purchase": "UNVERIFIED",
              "production_policy_changed": False}
    if publication is not None:
        _verify_record(publication, "PUBLICATION")
        if publication.get("race_id") != race_id or publication.get("final_sha256") != final_sha:
            raise ValueError("PUBLICATION_FINAL_BINDING_MISMATCH")
        result["publication_record"] = "HASH_AND_ID_MATCHED_NOT_REMOTE_VERIFIED"
    if availability is not None:
        if publication is None:
            raise ValueError("AVAILABILITY_WITHOUT_PUBLICATION")
        _verify_record(availability, "AVAILABILITY")
        if (availability.get("race_id") != race_id
                or availability.get("final_sha256") != final_sha
                or availability.get("tree_sha256") != publication.get("tree_sha256")):
            raise ValueError("AVAILABILITY_BINDING_MISMATCH")
        observed = _time(availability["availability_verified_at"])
        if availability.get("http_status") != 200:
            raise ValueError("AVAILABILITY_HTTP_NOT_OK")
        if availability.get("availability_verified_before_post") is not (observed < post):
            raise ValueError("AVAILABILITY_TEMPORAL_CLAIM_MISMATCH")
        result["canonical_availability"] = "READBACK_RECORDED"
        result["canonical_available_before_post"] = observed < post
        result["canonical_availability_verified_independently"] = False
    if notification is not None:
        _verify_record(notification, "NOTIFICATION")
        if (notification.get("race_id") != race_id
                or notification.get("final_sha256") != final_sha
                or not notification.get("provider_message_id")
                or notification.get("provider_status") != "ACCEPTED"):
            raise ValueError("NOTIFICATION_PROVIDER_EVIDENCE_INVALID")
        sent = _time(notification["provider_accepted_at"])
        result["notification_sent"] = "PROVIDER_ACCEPTED_RECORD_NOT_DELIVERY_PROOF"
        result["notification_before_post"] = sent < post
    if recipient_ack is not None:
        if notification is None:
            raise ValueError("RECIPIENT_ACK_WITHOUT_NOTIFICATION")
        _verify_record(recipient_ack, "RECIPIENT_ACK")
        if (recipient_ack.get("race_id") != race_id
                or recipient_ack.get("final_sha256") != final_sha
                or recipient_ack.get("provider_message_id") != notification["provider_message_id"]
                or recipient_ack.get("ack_status") != "RECEIVED"):
            raise ValueError("RECIPIENT_ACK_BINDING_INVALID")
        acknowledged = _time(recipient_ack["received_at"])
        if acknowledged < _time(notification["provider_accepted_at"]):
            raise ValueError("RECIPIENT_ACK_BEFORE_PROVIDER_ACCEPTANCE")
        result["recipient_acknowledged"] = "RECIPIENT_ACK_RECORD"
        result["pre_post_delivery"] = ("ACK_BEFORE_POST_RECORDED" if acknowledged < post
                                       else "ACK_AFTER_POST_RECORDED")
    result["evidence_scope"] = "SELF_HASHED_RECORDS_ONLY_NO_INDEPENDENT_TRUST_VERIFICATION"
    result["sha256"] = _sha(result)
    return result

def main(argv=None):
    """Inspect existing evidence only; never transmit, create, or re-sign it."""
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", type=Path, required=True)
    parser.add_argument("--publication", type=Path)
    parser.add_argument("--availability", type=Path)
    parser.add_argument("--notification", type=Path)
    parser.add_argument("--recipient-ack", type=Path)
    args = parser.parse_args(argv)
    def load(path):
        return json.loads(path.read_text(encoding="utf-8")) if path else None
    report = audit_delivery(
        final=load(args.final),
        publication=load(args.publication),
        availability=load(args.availability),
        notification=load(args.notification),
        recipient_ack=load(args.recipient_ack))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return report


if __name__ == "__main__":
    main()
