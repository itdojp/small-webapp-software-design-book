---
title: "05. 設計時にテストを織り込む"
permalink: /chapters/05-design-for-testability/
show_nav: true
prev: /chapters/04-minimal-architecture-ts/
next: /chapters/06-test-strategy-pyramid/
---

# 05. 設計時にテストを織り込む

## 目的

- テスト容易性を「後付け作業」にしないための設計原則を押さえる
- 観測できる振る舞い・境界・依存の扱いを整理し、保守性を上げる

## 得られる判断能力

- 何を単体で守り、何を統合/E2E で守るべきかを設計段階で判断できる
- 観測できる振る舞い（契約）にテストを寄せ、実装詳細依存を避けられる
- モック/スタブを「境界」に集中させ、テストの変更耐性を上げられる

## 前提/用語

- **検証可能性（テスタビリティ）**: 期待する結果が、テストで確実に合否判定できる性質（運用の「Observability」とは区別する）
- **CQS**: Command-Query Separation（状態変更と参照の分離）
- **スタブ/モック**: 外部依存を代替し、制御可能にする手段

## 要点

- テストは「内部実装」より「振る舞い（契約）」を守る
- 副作用境界を明確にし、コアは単体テストで守れる形にする
- モックが増える設計は、境界の置き方が不適切なシグナルになり得る

## 良いテストの4本柱（本書の評価軸）

本書では、自動テストを次の 4 観点で評価します。

- **価値**: 重要なリスク（価値導線、障害影響、損失）を守れているか
- **保守性**: 実装変更に強いか（テストが頻繁に壊れないか）
- **壊れにくさ**: 非決定性（時刻/乱数/外部I/O）によりフレークしないか
- **フィードバック速度**: 実行時間と診断容易性が適切か（失敗時に原因が追えるか）

## 統合テストの境界（本書の定義）

本書では「統合テスト」を、`domain/usecases` と `adapters` の境界を跨ぐ契約を検証するテストとして扱います（章 04 の最小アーキテクチャ前提）。

- 単体テストで無理に扱わない（統合で扱う）典型:
  - DB 永続化（スキーマ/クエリ/トランザクション）
  - HTTP 入出力（ルーティング、入力検証、エラー形式）
  - 認可（ロール/所有者ルールと API の接続）
  - 外部通知 I/F（失敗/遅延/リトライの扱い）
- 小規模での線引き（現実解）:
  - DB は「実物」を使い、repository adapter 経由で検証する
  - ネットワーク越しの外部サービスは、統合テストでは直接叩かず、adapter の契約をテストダブルで固定する（フレーク源になりやすい）
  - HTTP 入出力（入出力/エラー/冪等性）は API 契約として残すと、期待値（契約）が揃いやすい（任意: [Appendix B（B-14）]({{ '/appendix/B-templates/' | relative_url }}) / 記入例: [Appendix D（D-22）]({{ '/appendix/D-samples/' | relative_url }})）

## モック/スタブ方針（境界に寄せる）

モック/スタブは「依存を制御する」ための手段であり、設計上の境界を表します。本書の基本方針は次の通りです。

- `domain`: 原則としてテストダブル不要（純粋関数に寄せる）
  - 時刻/乱数などはグローバル参照せず、引数で受ける（例: `now: Date`）
- `usecases`: port（依存先インターフェース）を引数で受け、スタブ/フェイクで差し替える
  - 「呼ばれたこと」を見る必要がある場合は、最小のスパイ（呼び出し記録）に留める
  - 呼び出し順序や内部の回数など、契約でない要素をテストに含めない（変更耐性を落とす）
- `adapters`: I/O を含むため、統合テストで契約を検証する
  - 外部 I/F は adapter の入力/出力と失敗時の扱いを固定する（例: タイムアウト時は再送キューに積む。任意: [Appendix B（B-16）]({{ '/appendix/B-templates/' | relative_url }}) / 記入例: [Appendix D（D-24）]({{ '/appendix/D-samples/' | relative_url }})）

この方針で「モック地獄」を避けやすくなります。モックが増え続ける場合は、境界が薄い/責務が混ざっているサインとして扱ってください。

## 依存注入（依存を引数で受ける）

小規模 TS では、DI コンテナを導入する前に「依存を引数で受ける」だけで十分なことが多いです。

例: ユースケースが port を引数で受ける（疑似コード）

```ts
export type AssignTaskDeps = {
  now: () => Date;
  saveAssignment: (input: {
    taskId: string;
    assigneeId: string;
    assignedAt: Date;
  }) => Promise<void>;
  enqueueAssignedNotification: (input: {
    taskId: string;
    assigneeId: string;
    assignedAt: Date;
  }) => Promise<void>;
};

export async function assignTask(
  deps: AssignTaskDeps,
  input: { taskId: string; assigneeId: string }
): Promise<void> {
  const assignedAt = deps.now();
  await deps.saveAssignment({ ...input, assignedAt });
  // 送信そのものではなく、通知要求（outbox/queue等）の記録までを責務とする。
  await deps.enqueueAssignedNotification({ ...input, assignedAt });
}
```

テストでは `now/saveAssignment/enqueueAssignedNotification` をテストダブルに差し替え、外部 I/O を含まずに「期待する振る舞い」を検証できます。統合テストでは `saveAssignment` を実 DB に向け、通知要求の永続化（outbox等）を adapter の契約として検証します。

## 成果物駆動（仕様→テスト観点）

テスト容易性を上げる近道は「実装からテストを考える」のではなく、仕様（Behavior）を成果物として固定し、そこからテスト観点を導出することです。

本書では Appendix B のテンプレを次の順で使うことを推奨します。

1. **仕様（B-3）**: 受け入れ条件/例外系/観測点を確定する（何を見れば合否が分かるか）
2. **テスト観点（B-3内）**: 仕様の各項目から「守るべき契約」を箇条書きに落とす
3. **配分（B-8）**: その契約を単体/統合/E2E のどこで守るか決める

導出のコツ（B-3 → テスト観点）:

- 受け入れ条件（Given/When/Then）: 価値導線として E2E 候補になる（ただし外部I/Fは直接観測しない）
- 例外系/失敗時（Behavior）: 境界（認可、入力検証、競合、外部I/F）として統合テスト候補になる
- 観測点: 何を assert するかを決める（観測点が薄いとフレークと過剰モックが増える）

例（割り当て + 通知）での観点の出し方（抜粋）:

- 受け入れ条件: 「割り当てが成功し、UI 表示が更新される」→ E2E の最小導線
- 例外系: 「非管理者は `403`」→ 統合（HTTP+認可）の契約
- 外部I/F失敗: 「通知失敗でも業務継続し、検知と再送起点が残る」→ 統合（境界）の契約

## 例（ランニング例）

タスク管理では、次の分離がそのままテスト方針になります。

- domain（単体を厚く）:
  - 期限判定（期限超過/残日数）
  - 状態遷移（`todo → in_progress → done`）
  - 入力バリデーション（タイトル必須、期限形式）
- adapters（統合/E2E）:
  - DB（保存/検索）
  - メール送信（外部I/F、失敗/遅延）
  - 認可（ロール、所有者）

### CQS を小規模TSで扱う

- Query: 現在の状態を返す（副作用なし）
- Command: 状態を変える（副作用は境界に集約）

例: domain の Query（純粋）

```ts
export type DueStatus = "ok" | "due_soon" | "overdue";

export function calcDueStatus(now: Date, dueAt?: Date): DueStatus {
  if (!dueAt) return "ok";
  const diffMs = dueAt.getTime() - now.getTime();
  const dayMs = 24 * 60 * 60 * 1000; // 24時間（暦日基準ではない）
  if (diffMs < 0) return "overdue";
  if (diffMs <= 2 * dayMs) return "due_soon";
  return "ok";
}
```

補足: 「締切」や「日次バッチ」などが関わる場合、暦日（カレンダー日）での定義が必要になります。`24*60*60*1000` に依存する計算は、DST 等で意図とズレることがあるため、要件として定義してから実装してください。

例: 単体テスト（Vitest）

```ts
import { describe, it, expect } from "vitest";
import { calcDueStatus } from "./calcDueStatus";

describe("calcDueStatus", () => {
  it("期限なしは ok", () => {
    expect(calcDueStatus(new Date("2026-01-01T00:00:00Z"))).toBe("ok");
  });
  it("期限超過は overdue", () => {
    expect(
      calcDueStatus(
        new Date("2026-01-02T00:00:00Z"),
        new Date("2026-01-01T00:00:00Z")
      )
    ).toBe("overdue");
  });
});
```

ポイントは「時刻を引数で受ける」ことです。`Date.now()` を直接使うと、テストが非決定的になりやすいです。

## 演習（最小1個）

ランニング例のユースケースを 1 つ選び、次を分類してください。

1. 純粋（単体で厚く守る）: 入力→出力で検証できるもの
2. I/O（統合/E2E）: DB/HTTP/メールなど外部に依存するもの

分類結果をもとに、Appendix B の「仕様（Behavior）テンプレ（B-3）」のうち **テスト観点** を 5〜10 行で埋めてください。

- [Appendix B: テンプレ集（B-3. 仕様テンプレ）]({{ '/appendix/B-templates/' | relative_url }})
- 記入例: [Appendix D: 記入例]({{ '/appendix/D-samples/' | relative_url }})

例（選択肢）:

- タスク作成
- タスク割り当て（通知あり）
- タスク完了

## よくある失敗

- テストのために抽象化を増やし、設計が複雑化する（目的が逆転する）
- モックの状態がテストの本質になり、変更に弱くなる（モック地獄）
- 例外系の振る舞い（失敗時、ログ、リトライ）が曖昧なまま実装する

## チェックリスト

- [ ] 単体テスト対象（コア）と統合テスト対象（境界）が分けられている
- [ ] 統合テストの境界（DB/HTTP/認可/外部通知など）が列挙されている
- [ ] 例外系の振る舞いが要件・受け入れ条件と整合している
- [ ] モック/スタブの利用理由が説明できる（依存の制御）
- [ ] port（依存先）を引数で受けられる設計になっている（DI）
- [ ] テストが実装詳細ではなく振る舞い（契約）を検証している
- [ ] 非決定性（時刻、乱数、外部I/O）を制御できている
