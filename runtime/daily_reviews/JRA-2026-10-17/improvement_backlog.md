# Improvement Backlog

| Priority | ID | Route | Owner | Race数 | 次Action |
|---|---|---|---|---|---|
| P0 | R-BVI-BINDING | REPAIR_NOW | Runtime | 6 | Existing fix must be checked on latest main; do not duplicate; live acceptance remains separate |
| P0 | R-DISPATCH | REPAIR_NOW | Runtime | 1 | Use existing import-path repair; verify deployment workflow SHA |
| P0 | R-RESOLVER | REPAIR_NOW | Runtime | 1 | Do not re-execute expired R8; live acceptance pending |
| P0 | R-KRS-MEASUREMENT | REPAIR_NOW | Measurement | 23 | Implemented in this PR; Owner review/merge pending |
| P0 | P-DELIVERY | PROCESS_IMPROVEMENT | Runtime | 23 | Coordinate existing open PR302; no external message sent |
| P1 | H-WINNER | TEST_NEXT | JRA Family | 19 | Prepare Shadow protocol; Owner authorization before runtime activation |
| P1 | H-P2 | TEST_NEXT | JRA Family | 4 | Prepare Shadow protocol; Owner authorization before runtime activation |
| P2 | H-AKI | TEST_NEXT | JRA Family | 3 | Prepare Shadow protocol; Owner authorization before runtime activation |
| P2 | H-KRS | TEST_NEXT | JRA Family | 5 | Prepare Shadow protocol; Owner authorization before runtime activation |
| P2 | H-BVI | TEST_NEXT | JRA Family | 28 | Prepare Shadow protocol; Owner authorization before runtime activation |
| P2 | H-CAPITAL | TEST_NEXT | Family Common | 19 | Prepare Shadow protocol; Owner authorization before runtime activation |
| P1 | P-RESULT | PROCESS_IMPROVEMENT | Runtime | 17 | Prepare Shadow protocol; Owner authorization before runtime activation |
| P2 | D-FREEZE | DO_NOT_CHANGE | Family Common | 0 | PROMOTION_REVIEW only after current gates and Owner review |

詳細のEvidence/Regression/OOS/Promotion条件はimprovement_backlog.json。Production activation・Merge・通知送信は実施しない。

追加実行保証Review: [remaining_evidence_closure.md](remaining_evidence_closure.md)。KRS Output結合・送信bytes checkpoint・投資0保持の最小Correctness修復、Learning時刻検証、全36Failure Matrix、固定Shadow比較を保存。Merge/Activation・次Race消費は未確認。
