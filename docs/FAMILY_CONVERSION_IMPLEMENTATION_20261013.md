# 実装差分・検証・受入範囲

CANDIDATE / NON-PRODUCTION。既存Family Conversion Diagnosticsへopt-in測定を追加し、LOCAL既存Runnerが元AKI候補券面を渡して診断hashを既存FINAL traceへ束縛できるよう接続。新Selector/Capital Calculator/Validator/Workflow/失敗Classifierは作らない。

Correctness修復：非有限値/boolのPFS・Promotion・Learning入力除外、過去R43 statusの正確なGit blob凍結読出し、4 LOCAL場の測定上分類。期限失敗保存はPR263依存として別実装しない。

外部正本Runtimeは既存17戦FINAL/RESULT34件を/verifyで全件validと返した。新候補Code Deploy/Activation/新FINALは未実施。JRA/BANは共通金額schema回帰のみ、実レース受入・予測改善の証明ではない。

tests.log、production_tests.log、external_verification_status.json、runtime_health.json、production_freeze.jsonを参照。CIは専用PR作成後に確認。Authority/Selector/MEC/Capital/旧Signed FINAL/RESULT/17戦OOS台帳は変更なし。

Historical Measurement Acceptance != Forward Performance Acceptance。新候補Forward OOS0、配備/価格評価/等予算・等点数・No-Bet機会費用/全Family外部実行/Human ReviewはPENDING又はBLOCKED。

積み重ねPR：PR263をbaseにして既存のDeadline保存・旧7戦fixture修復を継承。共通PRに同じ修復コードを二重追加しない。
旧Phase B.2の本物のforward_protocol.jsonは変更しない。候補コードでは定義hashが異なるため旧研究captureはHOLDが正しい。pytestの機械試験だけはテスト用Protocol/一時Ledgerで結果前登録し、別版・別hashを使う。ドリフト拒否も回帰確認し、新研究OOSとして加算しない。
JRAの登録Runtime /healthはREADYだがEngine/parameter SHAを公開していない。BANはCurrent Runtime ContractでBLOCKED-PHYSICAL-RUNTIME-UNVERIFIED、登録外部endpointなし。共通schema成功を両Familyの外部正式受入れへ読み替えない。
