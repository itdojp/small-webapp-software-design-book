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
- 観察可能な振る舞い・境界・依存の扱いを整理し、保守性を上げる

## 得られる判断能力

- 何を単体で守り、何を統合/E2E で守るべきかを設計段階で判断できる
- 観察可能な振る舞い（契約）にテストを寄せ、実装詳細依存を避けられる
- モック/スタブを「境界」に集中させ、テストの変更耐性を上げられる

## 前提/用語

- **観察可能性**: 期待する結果が、テストで確実に検証できる性質
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
  const dayMs = 24 * 60 * 60 * 1000;
  if (diffMs < 0) return "overdue";
  if (diffMs <= 2 * dayMs) return "due_soon";
  return "ok";
}
```

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
- [ ] 例外系の振る舞いが要件・受け入れ条件と整合している
- [ ] モック/スタブの利用理由が説明できる（依存の制御）
- [ ] テストが実装詳細ではなく振る舞い（契約）を検証している
- [ ] 非決定性（時刻、乱数、外部I/O）を制御できている

## 前後リンク

- [目次]({{ '/chapters/' | relative_url }})
- [前章: 04. 小規模TS向けの最小アーキテクチャ]({{ '/chapters/04-minimal-architecture-ts/' | relative_url }})
- [次章: 06. テスト戦略（単体/統合/E2E）]({{ '/chapters/06-test-strategy-pyramid/' | relative_url }})
