---
title: "Appendix F: 全体概念依存マップ"
permalink: /appendix/F-concept-map/
show_nav: true
prev: /appendix/E-glossary/
next: /appendix/C-references/
---

# Appendix F: 全体概念依存マップ

本書の設計判断は、要求からテスト、進化条件までを独立に選ぶのではなく、前段の合意と分析を次段の入力にする流れで組み立てます。このページは、その**書籍全体の概念依存と章間の接続**を俯瞰し、目的に応じた読む順番を選ぶための索引です。

矢印の右側は、左側で得た判断や成果物を入力として使います。ただし一方向に完了させる工程表ではありません。テスト結果や変更要求から前段へ戻り、仕様、結合評価、境界を更新します。

## F-1. 非 JavaScript テキストマップ

次のマップはプレーンテキストであり、JavaScript が無効でも同じ順序と依存を確認できます。

```text
要求（目的・課題・KPI）                           [01]
  ↓ 目的と測定可能な価値を合意する
要件（Shall・制約・受け入れ条件）                   [01 / B-1〜B-2]
  ↓ 要件を外部から検証できる形へ具体化する
仕様（状態・入出力・観測可能な振る舞い）            [01 / B-3]
  ↓ 変更時に同時に動く箇所を洗い出す
相互作用・複雑性（波及範囲・不確実性）              [02]
  ↓ 重要な依存を比較可能にする
S/D/V による結合評価（統合強度・距離・変動性）      [03]
  ↓ 一体化・分離・契約固定の手当を選ぶ
アーキテクチャ境界（domain / usecases / adapters）  [04]
  ↓ 副作用と依存を制御し、観測点を置ける形にする
テスト容易性（注入・決定性・境界契約）              [05]
  ↓ 守る対象を適切な粒度へ配分する
テスト戦略（単体 / 統合 / E2E）                    [06]
  ↓ 実行結果と変化の兆候を次の判断へ戻す
進化条件・ADR（強化時機・意思決定・帰結）           [07 / B-6〜B-7]
  └──────── 新しい要求・仕様・結合評価へフィードバック ────────┘
```

最短の主系列は `01 → 02 → 03 → 04 → 05 → 06 → 07` です。Appendix B は各段階の判断を記録するテンプレート、Appendix D は同じ成果物をランニング例で確認する記入例として併用します。

## F-2. 等価な概念依存表

テキストマップと同じ依存を表形式で示します。表の「必要な入力」が一つ前の段階、「次へ渡すもの」が矢印の出力に対応します。

| 段階 | 必要な入力 | 判断する問い | 次へ渡すもの | 主な参照先 |
| --- | --- | --- | --- | --- |
| 要求 | 課題、利用者、事業目的 | なぜ行うか、何を測れば価値を確認できるか | 目的、KPI、スコープ、非ゴール | [01. 要件定義を設計入力にする]({{ site.baseurl }}/chapters/01-requirements-as-input/) |
| 要件 | 合意した要求 | 何を満たす必要があり、どの制約と受け入れ条件を守るか | Shall、制約、受け入れ条件 | [01章]({{ site.baseurl }}/chapters/01-requirements-as-input/)、[Appendix B-1〜B-2]({{ site.baseurl }}/appendix/B-templates/) |
| 仕様 | 合意した要件 | 要件を外部からどのように観測・検証できる形へ具体化するか | 状態、入出力、正常時・失敗時の振る舞い | [01章]({{ site.baseurl }}/chapters/01-requirements-as-input/)、[Appendix B-3]({{ site.baseurl }}/appendix/B-templates/) |
| 相互作用・複雑性 | 変更可能性のある要件・仕様 | 変更は UI、API、DB、外部I/F、運用、テストのどこへ波及するか | 変更シナリオ、波及先、観測点、設計の焦点 | [02. 複雑性の捉え方]({{ site.baseurl }}/chapters/02-complexity-and-interaction/) |
| S/D/V による結合評価 | 焦点化した相互作用 | 統合強度、距離、変動性のどこが変更コストを高めるか | 一体化、分離、契約固定などの手当候補 | [03. 結合の物差し]({{ site.baseurl }}/chapters/03-coupling-balance-sdv/) |
| アーキテクチャ境界 | 手当対象の依存と制約 | どの責務を同じ場所に置き、どの依存方向を固定するか | domain、usecases、adapters、port、境界契約 | [04. 最小アーキテクチャ]({{ site.baseurl }}/chapters/04-minimal-architecture-ts/) |
| テスト容易性 | 境界、契約、観測点 | 副作用を制御し、期待結果を決定的に観測できるか | 注入可能な依存、純粋なコア、境界別の検証点 | [05. 設計時にテストを織り込む]({{ site.baseurl }}/chapters/05-design-for-testability/) |
| テスト戦略 | 守る契約と価値導線 | 何を単体、統合、E2E のどこで守るか | テスト配分、実行結果、未検証範囲 | [06. テスト戦略]({{ site.baseurl }}/chapters/06-test-strategy-pyramid/) |
| 進化条件・ADR | テスト結果、運用事実、新しい変更要求 | いつ境界を強化し、どの判断と帰結を残すか | Change Drivers、ADR、次の要求・仕様・結合評価 | [07. 進化条件]({{ site.baseurl }}/chapters/07-evolution-and-adr/) |

## F-3. 目的別ルート

通読せずに課題から入る場合も、先に必要な概念へ戻れる順序で参照します。

| 目的・症状 | 推奨ルート | 到達する判断 |
| --- | --- | --- |
| 要望が実装案へ直結し、合意範囲が曖昧 | [01章]({{ site.baseurl }}/chapters/01-requirements-as-input/) → [02章]({{ site.baseurl }}/chapters/02-complexity-and-interaction/) | 要求、要件、仕様を分け、変更の波及を確認する |
| 変更のたびに複数箇所が壊れる | [02章]({{ site.baseurl }}/chapters/02-complexity-and-interaction/) → [03章]({{ site.baseurl }}/chapters/03-coupling-balance-sdv/) → [04章]({{ site.baseurl }}/chapters/04-minimal-architecture-ts/) | 相互作用を焦点化し、結合への最小の手当と境界を選ぶ |
| テストが書きにくい、またはモックが増え続ける | [04章]({{ site.baseurl }}/chapters/04-minimal-architecture-ts/) → [05章]({{ site.baseurl }}/chapters/05-design-for-testability/) | 依存方向と副作用の置き場所を見直し、観測可能な契約を作る |
| 単体、統合、E2E の配分を決めたい | [05章]({{ site.baseurl }}/chapters/05-design-for-testability/) → [06章]({{ site.baseurl }}/chapters/06-test-strategy-pyramid/) | 境界と価値導線に対応したテスト粒度を選ぶ |
| 抽象化や境界強化の時機を判断したい | [03章]({{ site.baseurl }}/chapters/03-coupling-balance-sdv/) → [04章]({{ site.baseurl }}/chapters/04-minimal-architecture-ts/) → [07章]({{ site.baseurl }}/chapters/07-evolution-and-adr/) | Change Drivers を根拠に変更し、ADR に判断と帰結を残す |
| 自分の案件へ一連の成果物を適用したい | [Appendix A]({{ site.baseurl }}/appendix/A-checklists/) → [Appendix B]({{ site.baseurl }}/appendix/B-templates/) → [Appendix D]({{ site.baseurl }}/appendix/D-samples/) | 漏れを確認し、テンプレートを記入例と照合して運用する |

途中の段階から入って前提が決まっていないことに気付いた場合は、表の「必要な入力」をたどって左側の段階へ戻ります。例えばテスト配分を決められない場合、テストの本数を先に決めず、守る境界と観測可能な仕様があるかを確認します。

## F-4. 局所的な相互作用マップとの責務の違い

この全体概念依存マップと、[02章]({{ '/chapters/02-complexity-and-interaction/' | relative_url }})、[Appendix B-9]({{ '/appendix/B-templates/' | relative_url }})、[Appendix D-17]({{ '/appendix/D-samples/' | relative_url }}) の相互作用マップは用途が異なります。

| マップ | 対象範囲 | 使う時点 | 読者が得るもの |
| --- | --- | --- | --- |
| Appendix F（このページ） | 書籍全体の概念と章間依存 | 読む入口、判断手順を見失った時 | 前提概念、次に読む章、目的別ルート |
| 02章の相互作用整理 | 1 つの変更シナリオと波及範囲 | 要件・仕様の変更影響を分析する時 | 設計の焦点となる相互作用 |
| Appendix B-9 | 局所分析を案件で記録するテンプレート | 相互作用分析を成果物として残す時 | 変更、波及、観測、制約候補の記入欄 |
| Appendix D-17 | B-9 を期限・通知シナリオへ適用した記入例 | テンプレートの粒度を確認する時 | 局所マップの具体的な完成イメージ |

Appendix F を案件ごとの相互作用分析の代わりには使いません。反対に、B-9 や D-17 の 1 シナリオだけで本書の概念依存を説明したことにもなりません。全体の読む順序は Appendix F、案件固有の変更分析は 02章と B-9、具体例の確認は D-17 と使い分けます。

## F-5. 反復するときの戻り先

- テストで期待結果を定義できない場合: 要件・仕様の観測可能性へ戻る
- 統合テストが広範囲に壊れる場合: 相互作用と S/D/V を再評価する
- 外部I/Fの失敗で業務判断が揺れる場合: 境界契約と失敗時の仕様へ戻る
- 抽象化の維持コストが高い場合: 進化条件と ADR の前提を見直す
- 新しい要求が追加された場合: 既存 ADR を絶対視せず、主系列を要求から再実行する

この反復により、ADR は設計を固定する終点ではなく、次の要求・仕様・結合評価へ判断根拠を引き継ぐ接続点になります。
