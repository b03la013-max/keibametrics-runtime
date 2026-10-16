# Mac-local Keibabook collector — user-authorized subscription only

## Purpose and status

On a Mac, Playwright's dedicated Chromium profile retains **the subscriber's own authenticated browser session**. Once a race has been queued with its correct Book race ID and independently prepared official runner list, macOS `launchd` can fetch the Book ability/workout/stable pages **before the race cutoff**, validate matching horse numbers/names, parse with the *existing* authenticated-private intake, evaluate the four existing registered feature bands, and save results only on that Mac.

This code does **not** bypass login, CAPTCHA, MFA, a refusal to allow automation, or paid access. Keibabook states that unauthorized reproduction, storage or redistribution is prohibited. Before enabling page retention or scheduled collection, the subscriber needs to verify that this particular use is permitted by the provider. There is no authorization assertion in this code.

The three pages already established by the Work intake are:

- `https://s.keibabook.co.jp/cyuou/nouryoku_html_detail/<12-digit race ID>.html`
- `https://s.keibabook.co.jp/cyuou/cyokyo/0/<12-digit race ID>`
- `https://s.keibabook.co.jp/cyuou/danwa/0/<12-digit race ID>`

The collector does not try to derive a 12-digit Book race ID from an unrelated JRA meeting ID: guessing can capture the wrong race. An upstream authoritative race-link discovery and verified JRA SOURCE-to-queue connection **remain necessary** before true all-race zero-touch orchestration.

## One-time Mac setup (when subscriber has provider permission)

```sh
cd ~/keibametrics-runtime
python3 -m venv .venv
source .venv/bin/activate
python -m pip install playwright beautifulsoup4
python -m playwright install chromium
python runtime/jra_keibabook_mac_collector.py login
```

In the new **separate**, visible Chromium window, sign in normally to the subscriber site, then press Enter in Terminal. Do not enter credentials, cookies, OTP or session exports into ChatGPT, GitHub or cloud logs. The browser profile is stored under `~/.keibametrics/browser_keibabook`, with restricted local permissions. Playwright's official guidance also warns that session state is highly sensitive.

Before running, write a private queue at `~/.keibametrics/book_queue.json` (mode 0600) containing events with authoritative pre-cutoff identity references:

```json
[
  {
    "book_race_id": "202604000309",
    "race_date": "2026-10-10",
    "prediction_cutoff": "2026-10-10T14:10:00+09:00",
    "official_runners_path": "/Users/YOU/.keibametrics/official_runners_kyo_r09.json"
  }
]
```

This is a **past historical example only**. Any current run with that cutoff skips it instead of mislabeling late capture as a forward prediction. `official_runners_path` must be independently generated from the JRA Signed SOURCE universe. The program checks the supplied runner numbers/names against Book pages but **does not itself establish upstream Source signing or OIDC authenticity**. Never create an official list from the same Book page to self-verify.

Run a single capture for an eligible future race:

```sh
python runtime/jra_keibabook_mac_collector.py capture \
  --spec ~/.keibametrics/future_book_race_spec.json
```

Or make macOS poll the queue (every five minutes) with:

```sh
python runtime/jra_keibabook_mac_collector.py install-launchd --activate
```

The Mac must be **powered on, awake, online**, logged in to the dedicated browser profile, and the Book subscription must remain valid. `launchd` runs local commands; it cannot force a sleeping device to fetch content. If authentication expires or access is denied, the job records a failure and never forges a successful capture.

Capture output: `~/.keibametrics/private_book/<book_race_id>/` is local-only and immutable. It contains the local browser-rendered page copies, SHA-256 capture manifest, the parsed private intake, diagnostic four-band evaluator result and a nonpaid summary. Do not add this directory to the git repo or upload paid raw content to CI, Railway or GitHub. The recorded hash proves **the saved bytes**, not server signature or provider certification. Re-running an already committed race is rejected. Partial failures are discarded.

The collector is intentionally `NON-PRODUCTION / NO AUTO-PURCHASE / NO SIGNED FINAL`. Additional implementation is needed to use any provider-permitted facts in an authenticated SOURCE-side Production evaluator and to demonstrate Full20; *collection alone* does not confer numeric or Static approval.

### Automated pipeline still to close

1. Provider-permitted subscription acquisition and race-ID link discovery for arbitrary future JRA cards.
2. JRA Signed SOURCE verified winner-independent runner universe and cutoff -> private queue with race-to-race ID binding and independent attestation.
3. Private **permitted** feature evidence -> governed Production SOURCE/Evidence binding without publishing subscriber material.
4. Base13/Derived7 calculation and Static Authority review; only then KRS, MEC, Capital, FINAL.
