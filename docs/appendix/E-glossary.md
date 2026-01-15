---
title: "Appendix E: 用語集"
permalink: /appendix/E-glossary/
show_nav: true
prev: /appendix/D-samples/
next: /appendix/C-references/
---

# Appendix E: 用語集

本書で繰り返し登場する用語を、最小の定義として整理します。厳密な学術定義ではなく、本書の判断（要求→要件→仕様→設計→テスト）を揃えるための用語集です。

## E-1. 要件/合意

- **要求（Needs / Goals）**: なぜやるか（ビジネス目的・課題・KPI）。未整理で矛盾を含み得るため、目的と測定（KPI）に落とす
  - 関連: [01. 要件定義を設計入力にする]({{ '/chapters/01-requirements-as-input/' | relative_url }})
- **要件（Requirements / Shall）**: 何を満たすべきか（実装方法に依存しない約束）。「〜できること」「〜しなければならない」を列挙する
  - 関連: [01. 要件定義を設計入力にする]({{ '/chapters/01-requirements-as-input/' | relative_url }})
- **仕様（Specification / Behavior）**: どう振る舞うか（外部から観測できる振る舞いを曖昧さなく）。入力/出力、状態遷移、エラー形式などを定義する
  - 関連: [Appendix B: テンプレ集]({{ '/appendix/B-templates/' | relative_url }})
- **設計（Design / Structure）**: どう作るか（内部構造・モジュール・アルゴリズム・DB物理など）。仕様を満たすための構造を決める
  - 関連: [04. 小規模TS向けの最小アーキテクチャ]({{ '/chapters/04-minimal-architecture-ts/' | relative_url }})
- **受け入れ条件**: 検証可能な合否基準（Given/When/Then など）
  - 関連: [Appendix B: テンプレ集]({{ '/appendix/B-templates/' | relative_url }})
- **観測点**: 合否判定のために「何を見ればよいか」を固定したポイント（画面表示、APIレスポンス、ログ、イベント等）
  - 関連: [Appendix B: テンプレ集]({{ '/appendix/B-templates/' | relative_url }})
- **非機能（NFR）**: 性能、可用性、セキュリティ、運用性などの制約条件
  - 関連: [01. 要件定義を設計入力にする]({{ '/chapters/01-requirements-as-input/' | relative_url }})
- **価値導線**: ユーザー価値を成立させる主要な利用フロー（止まると損失が大きい導線）
  - 関連: [06. テスト戦略（単体/統合/E2E）]({{ '/chapters/06-test-strategy-pyramid/' | relative_url }})

## E-2. 設計/境界

- **相互作用**: ある変更が別の箇所に波及する関係（暗黙依存を含む）
  - 関連: [02. 複雑性の捉え方]({{ '/chapters/02-complexity-and-interaction/' | relative_url }})
- **境界**: 依存方向を固定し、相互作用を制御する線引き（責務分離点）
  - 関連: [04. 小規模TS向けの最小アーキテクチャ]({{ '/chapters/04-minimal-architecture-ts/' | relative_url }})
- **契約**: 境界を跨ぐ入出力・失敗時の扱い・互換性などの合意（文書/型/テストで固定する）
  - 関連: [05. 設計時にテストを織り込む]({{ '/chapters/05-design-for-testability/' | relative_url }})
- **冪等性（Idempotency）**: 同じ操作を繰り返しても、結果が重複しない性質（例: 二重送信でデータや通知が増殖しない）
  - 関連: [01. 要件定義を設計入力にする]({{ '/chapters/01-requirements-as-input/' | relative_url }})
- **S/D/V**: 結合を扱うための物差し（統合強度 / 距離 / 変動性）
  - 関連: [03. 結合の物差し（S/D/V）]({{ '/chapters/03-coupling-balance-sdv/' | relative_url }})
- **Functional core / Thin shell**: 副作用のないコアと、I/O を担うシェルの分離方針
  - 関連: [04. 小規模TS向けの最小アーキテクチャ]({{ '/chapters/04-minimal-architecture-ts/' | relative_url }})
- **adapter**: DB/HTTP/外部I/F などの I/O を担う実装（境界の外側）
  - 関連: [04. 小規模TS向けの最小アーキテクチャ]({{ '/chapters/04-minimal-architecture-ts/' | relative_url }})
- **port**: adapter を抽象化した「依存先インターフェース」（ユースケース側が引数で受ける）
  - 関連: [05. 設計時にテストを織り込む]({{ '/chapters/05-design-for-testability/' | relative_url }})

## E-3. テスト

- **単体テスト**: 小さい単位（関数/モジュール）で振る舞い（契約）を検証する
  - 関連: [06. テスト戦略（単体/統合/E2E）]({{ '/chapters/06-test-strategy-pyramid/' | relative_url }})
- **統合テスト**: 境界を跨ぐ契約（DB/HTTP/認可/外部連携）を検証する
  - 関連: [05. 設計時にテストを織り込む]({{ '/chapters/05-design-for-testability/' | relative_url }})
- **E2E**: ユーザー導線として価値を提供できることを検証する（少数精鋭）
  - 関連: [06. テスト戦略（単体/統合/E2E）]({{ '/chapters/06-test-strategy-pyramid/' | relative_url }})
- **モック/スタブ**: 外部依存を代替し、制御可能にする手段（境界に寄せる）
  - 関連: [05. 設計時にテストを織り込む]({{ '/chapters/05-design-for-testability/' | relative_url }})
- **フレーク**: 非決定性（時刻/データ/外部I/O/待機）により、テスト結果が不安定になること
  - 関連: [06. テスト戦略（単体/統合/E2E）]({{ '/chapters/06-test-strategy-pyramid/' | relative_url }})

## E-4. 意思決定/運用

- **ADR**: Architecture Decision Record（意思決定の記録）
  - 関連: [07. 進化条件（ADRと境界の強化タイミング）]({{ '/chapters/07-evolution-and-adr/' | relative_url }})
- **Change Drivers**: 「なぜ今変えるか」を整理するドライバー（S/D/V、運用要件、組織等）
  - 関連: [Appendix B: テンプレ集]({{ '/appendix/B-templates/' | relative_url }})
- **観測性**: 期待する結果が、テスト・ログ・メトリクス等で確実に検証できる性質
  - 関連: [05. 設計時にテストを織り込む]({{ '/chapters/05-design-for-testability/' | relative_url }})
- **相関ID（Correlation ID）**: 複数のログ/イベントを同一の処理として関連付ける識別子（障害解析・監査に用いる）
  - 関連: [07. 進化条件（ADRと境界の強化タイミング）]({{ '/chapters/07-evolution-and-adr/' | relative_url }})
