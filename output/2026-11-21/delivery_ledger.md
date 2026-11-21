# 地方版 配送台帳 2026-11-21（19:36時点）

- 管理Race 23／発走済み 17
- PAPER：凍結 23・Push検証 23・送信 15（発走前 15）・読み戻し一致 15・本人確認 0
- 正式：試行 15・Signed FINAL 14（NO-BET 0）・発走前送信 14・読み戻し一致 14・本人確認 0
- 発走前PAPER配送なしで発走：['KOC_01', 'KOC_02', 'KOC_03', 'SAG_01', 'SAG_02', 'SAG_03']
- 発走前の正式配送なしで発走（未試行を含む）：['KOC_01', 'KOC_02', 'KOC_03', 'KOC_04', 'SAG_01', 'SAG_02', 'SAG_03']
- 正式の停止工程：{'KOC_04': 'SOURCE_FREEZE'}
- 10分前チェック：確認 11／重要変更 9／Revision 2署名 9
- 停止工程：{'KOC_01': 'DELIVERY_SUBMITTED', 'KOC_02': 'DELIVERY_SUBMITTED', 'KOC_03': 'DELIVERY_SUBMITTED', 'SAG_01': 'DELIVERY_SUBMITTED', 'SAG_02': 'DELIVERY_SUBMITTED', 'SAG_03': 'DELIVERY_SUBMITTED'}／配送再試行：なし

| Race | 発走 | 状態 | PAPER送信 | 発走前 | 正式 | 正式送信 | 発走前 | 停止工程 |
|---|---|---|---|---|---|---|---|---|
| KOC_01 | 14:55 | POSTRESULT_DIAGNOSTIC |  | × | - | - | - | DELIVERY_SUBMITTED |
| KOC_02 | 15:30 | POSTRESULT_DIAGNOSTIC |  | × | - | - | - | DELIVERY_SUBMITTED |
| KOC_03 | 16:05 | POSTRESULT_DIAGNOSTIC |  | × | - | - | - | DELIVERY_SUBMITTED |
| KOC_04 | 16:40 | POSTRESULT_DIAGNOSTIC | 16:28 | ○ | HOLD |  | × |  |
| KOC_05 | 17:15 | POSTRESULT_DIAGNOSTIC | 16:34 | ○ | SIGNED_FINAL | 17:05 | ○ |  |
| KOC_06 | 17:45 | POSTRESULT_DIAGNOSTIC | 17:01 | ○ | SIGNED_FINAL | 17:02 | ○ |  |
| KOC_07 | 18:15 | POSTRESULT_DIAGNOSTIC | 17:30 | ○ | SIGNED_FINAL | 18:06 | ○ |  |
| KOC_08 | 18:45 | POSTRESULT_DIAGNOSTIC | 18:01 | ○ | SIGNED_FINAL | 18:37 | ○ |  |
| KOC_09 | 19:20 | PRESTART_PUSH_VERIFIED | 18:39 | ○ | SIGNED_FINAL | 19:10 | ○ |  |
| KOC_10 | 19:50 | PRESTART_PUSH_VERIFIED | 19:06 | ○ | SIGNED_FINAL | 19:07 | ○ |  |
| KOC_11 | 20:20 | PRESTART_PUSH_VERIFIED | 19:35 | ○ | SIGNED_FINAL | 19:36 | ○ |  |
| KOC_12 | 20:50 | PRESTART_PUSH_VERIFIED |  | … | - | - | - |  |
| SAG_01 | 15:25 | POSTRESULT_DIAGNOSTIC |  | × | - | - | - | DELIVERY_SUBMITTED |
| SAG_02 | 15:55 | POSTRESULT_DIAGNOSTIC |  | × | - | - | - | DELIVERY_SUBMITTED |
| SAG_03 | 16:30 | POSTRESULT_DIAGNOSTIC |  | × | - | - | - | DELIVERY_SUBMITTED |
| SAG_04 | 17:05 | POSTRESULT_DIAGNOSTIC | 16:30 | ○ | SIGNED_FINAL | 16:55 | ○ |  |
| SAG_05 | 17:35 | POSTRESULT_DIAGNOSTIC | 16:52 | ○ | SIGNED_FINAL | 17:27 | ○ |  |
| SAG_06 | 18:10 | POSTRESULT_DIAGNOSTIC | 17:28 | ○ | SIGNED_FINAL | 18:01 | ○ |  |
| SAG_07 | 18:40 | POSTRESULT_DIAGNOSTIC | 17:57 | ○ | SIGNED_FINAL | 17:58 | ○ |  |
| SAG_08 | 19:10 | POSTRESULT_DIAGNOSTIC | 18:26 | ○ | SIGNED_FINAL | 19:00 | ○ |  |
| SAG_09 | 19:40 | PRESTART_PUSH_VERIFIED | 18:56 | ○ | SIGNED_FINAL | 19:30 | ○ |  |
| SAG_10 | 20:10 | PRESTART_PUSH_VERIFIED | 19:26 | ○ | SIGNED_FINAL | 19:27 | ○ |  |
| SAG_11 | 20:40 | PRESTART_PUSH_VERIFIED |  | … | - | - | - |  |

<sub>USER_REACHED counts only the Owner's own confirmation; GitHub post/read-back is not proof of reading.</sub>
