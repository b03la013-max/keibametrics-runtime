# LOCAL Input / Source Operations v1.4

Profile: `KM-LOCAL-INPUT-SOURCE-OPS-v1.4-20260923`  
Predecessor: `KM-LOCAL-INPUT-SOURCE-OPS-v1.3-20260923`  
Status: ACTIVE / LOCAL-WIDE / NON-NUMERICAL / SIGNED-SOURCE-ACQUISITION / AUTOMATIC-NAR-MANIFEST / FAIL-CLOSED

## 0. Purpose

LOCAL Formal PredictionのSource取得を、手入力URL依存ではなくRace Metadataから再現可能にする。

```text
venue_id + race_date + race_no + prediction_cutoff
→ LOCAL NAR Source Manifest
→ NAR Official HTTPS Fetch
→ Raw Snapshot
→ Structured Evidence
→ SOURCE Freeze
→ Signed SOURCE Receipt
```

Prediction Model、指数式、KRS Engine、parameter_map、MEC、Capital Authorityは変更しない。

## 1. Automatic LOCAL NAR Manifest

Profile: `KM-LOCAL-NAR-SOURCE-MANIFEST-v1.0-20260923`

正式LOCAL routeでは、明示的Required Source Manifestが与えられていない場合でも、次のmetadataが揃えばRuntimeがNAR公式Manifestを生成できる。

- venue_id
- race_date
- race_no
- prediction_cutoff
- race_id

対応LOCAL Venue：

- MOR 盛岡
- MIZ 水沢
- URW 浦和
- FNB 船橋
- OHI 大井
- KAW 川崎
- KNZ 金沢
- KSM 笠松
- NGY 名古屋
- SON 園田
- HIM 姫路
- KCH 高知
- SAG 佐賀
- MON 門別

BANのOBIはLOCAL Adapterへ入れない。

## 2. Initial NAR Source Set

Required:

- NAR Official Race Card / DebaTable
- race card内の馬体重・増減・変更情報
- race card内で公表されている現在馬場・天候・発走時刻等

Optional:

- NAR Official Tan/Fuku Odds
- 当該Raceより前に終了済みの同日公式Result / Passing Order

Optional Sourceの取得失敗はSnapshotへ明示保存するが、それだけでFormal全体を停止しない。
Required Sourceの欠落・HTTP失敗・Required Extraction失敗はFail-Closedする。

## 3. Evidence Scope

同日複数Raceの結果を同一Evidence Fieldへ潰してはならない。

例：

- same_day_r01_result_tables
- same_day_r01_weather
- same_day_r01_track_condition
- same_day_r02_result_tables
- same_day_r02_weather
- same_day_r02_track_condition

異なるRaceの異なる事実はConflictではなく別scopeである。
同一scope・同一Evidence Field・同Priority Authorityで値が競合した場合のみUNRESOLVED Conflictとする。

## 4. Raw / Parsed Separation

Raw Source bodyとParsed Evidenceを分離し、最低限次を保持する。

- requested_url
- final_url
- http_status
- content_type
- fetched_at
- cutoff_relation
- raw_sha256
- raw_gzip_b64
- extracted_evidence
- snapshot_sha256

HTML tableは構造化Tableとして抽出可能だが、Raw bodyを廃棄しない。

## 5. Temporal Rules

FORMAL-PRE-RACEではRequired SourceのPOST_CUTOFF混入を禁止する。
過去RaceをAcceptance Fixtureとして取得する場合でも、Acceptance用cutoffはProduction Forecastの時点意味とは区別して記録する。

## 6. Security

- HTTPS only
- allowlisted NAR host
- redirect先再検査
- private/loopback/link-local/reserved IP拒否
- response size上限
- timeout
- content type制限
- arbitrary Authorization header禁止

## 7. Live Acceptance

GitHub Actions run `35767750170` でPASS。

Fixture:
- venue: KCH 高知
- race date: 2026-09-13
- race no: 3
- manifest source count: 4
- required NAR Race Card: HTTP 200
- structured race card tables: 2
- KRS actual_run_count: 5,000

Receipts:
- SOURCE: `be29d089097a738f829068165c74ae94c8362cc2f6933781cf675a03bd21afee`
- PRE_KRS: `ac20a0851ae608ec77ac221ec35c7b38544ed323dc7b03a16540561e502bf146`
- KRS: `1d917097bcae8102f8da44e727c884698fe1a5ec25d3f7569ca0558718fc3dd0`
- FINAL: `4ea4625e6c0761b472580462967d1f9a9d958a5b7172a269967e23270fa943cb`
- FORMAL: `e63b44bf0dd7e7f121f7d9722cb7406a267510d32339f804fc66757b614faf1e`

Race card raw SHA256:
`4bba2299550d6db7b29dda0880f547255281ccb43198afc6bca9c3ee192a4826`

Source Snapshot SHA256:
`bf50374204c76f89881a35b6443be3d930b885d62ebbfa9246b2e94d0be89230`

## 8. Boundary

このAcceptanceはNAR AdapterとSource-to-Formal機械接続の実証である。
未知未来の実在Raceについて、発走前に取得・予測・購入候補Freezeし、結果後にSettlementまで閉じた最初のReal-Race Empirical Acceptanceとは別であり、後者はPENDINGを維持する。
