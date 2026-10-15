# PR280 Owner本人の確認対象（未確認として記録）

コード対象：655530735f24cce78605dd1bd34843bdb2ea253d。最新main：523b9360284e9e00e5b49771e79f06dbb5189757。

Ownerの今回の指示を方式の正式化根拠として記録する。ただしOwner本人が下記を実際に確認したという申告はまだない。Workはその人間の確認を代行しない。独立Human Reviewは未実施。以下の確認と対象SHAへの明示リリース承認が第一停止工程。

| Owner確認対象 | 実差分・影響 | 残るリスクと停止/復旧 |
|---|---|---|
| SOURCE/Checkpoint/FINAL | 原SOURCEの再利用、既存FINALの署名検証と読戻し。新しい予測にすり替えない | 不一致時HOLD。再生成で通さない |
| 公式取消とActive | 取消根拠が署名SOURCE内のofficial/PRE_CUTOFF資料を参照することを検証 | 公式根拠が不足するRaceは止まる。正常に通るLIVEは未実証 |
| MEC/FINAL境界 | Active外のranking/Role/Pair/Third/券面参照を署名前拒否。MECの選択式・Capital配分変更なし | 既存の不正参照が顕在化しFINAL不成立となり得る。安全チェックは解除しない |
| Settlement | 的中払戻欠落/非正を0円COMPLETEにしない | 結果/払戻未確定はHOLD、実購入PFS UNKNOWN |
| Scheduling | KAW10/16R01のみ、14:00/05/10の3機会。1Dispatch/同時1、曖昧再送0 | GitHub開始遅延は保証不可。3preflight tick内部で既存Health transportは最大12試行となる。通常成功後は再予測しない |
| 費用 | 既存共有WorkspaceのHobby/soft/hard上限を維持 | Workspace上限は専用Race予算ではなく、上限到達時は共有サービス停止の可能性。追加実行単価は個別計測不能 |
| wrapper配置 | 旧f0d23766のroot11モジュール等を維持しapp_v15.pyだけを差替え、Gatewayを整合 | current main全体をRuntimeへ配置しない。途中不一致は受付HOLD、旧startCommand/GatewayへRollback |

## 具体的に確認する差分

- GitHub PR280 Files changed（現在60パス）。旧59パスからの追加はevidence回帰log1件、変更は既存Workflow2本。Executionコードの追加変更なし。
- runtime/local_physical/app_v15.py、local_production_static_owner.py、minimum_efficient_coverage.py、local_result_from_signed_final.py、local_race_entry.py、local_race_key_gate.py、local_race_key_intake.py、local_race_day_dispatcher.py。
- 既存release資料、59→60パス分類、回帰465+13subtests、CI14 Workflow/16check。
- PR282 evidence/kaw_phase_b_low_cost_20261015 のHEAD固定startCommand/Gateway/rollback案。

## Owner確認後の実行範囲

Owner本人が上記差分・リスク・Rollbackを確認し、対象HEADのMergeを明示承認した記録を得た後、最新HEAD/CI/Authority/費用/期限を再照合して進む。Deployと限定Activationの実行方針は今回の依頼に含まれるが、前提未成立中は実行しない。変更があれば該当承認を再照合する。

KAW2026-10-16R01、Runtime既存endpoint、既存全必要payload、最大1Dispatch/同時1/Preflight3/曖昧再送0のみ。他11Race、他Venue/JRA/BANへの送信なし。公式情報は実行前にfresh再取得。今回の公式メニュー再取得は404で失敗しており、Active/Material ChangeをPASSとしない。
