---
title: "04. 小規模TS向けの最小アーキテクチャ"
permalink: /chapters/04-minimal-architecture-ts/
show_nav: true
prev: /chapters/03-coupling-balance-sdv/
next: /chapters/05-design-for-testability/
---

# 04. 小規模TS向けの最小アーキテクチャ

## 目的

- 小規模で有効な「最小の境界」を定義し、設計・テストに接続する
- Functional core / thin shell の考え方で、変更容易性と実装速度を両立する

## 得られる判断能力

- 小規模で必要十分な境界（責務分離）を定義できる
- 「コア（純粋ロジック）」と「シェル（I/O）」の分割方針を説明できる
- 依存の向きを固定し、テスト戦略（単体/統合）に接続できる

## 前提/用語

- **Functional core**: 副作用のないロジック（入力→出力が決まる）
- **Thin shell**: I/O、フレームワーク、状態管理など副作用を担う層
- **境界**: 依存方向を固定し、相互作用を制御する線引き

## 要点

- 小規模では「層を増やす」より「責務を分ける」ことを優先する
- 状態は必要最小限にし、コアに押し込めない（コアは状態に依存しない）
- 境界はテスト方針（どこを単体で守るか）とセットで決める

## 例（ランニング例）

タスク管理を「最小の境界」で扱う場合、以下の 3 つに分けるだけでも効果が出ます。

- `domain/`: 期限判定、状態遷移、バリデーションなど（副作用なし）
- `usecases/`: ユースケース（登録/割り当て/完了）をオーケストレーション（依存は引数で受ける）
- `adapters/`: HTTP/DB/メール等の I/O

例: 状態遷移の domain 関数（純粋）

```ts
export type TaskStatus = "todo" | "in_progress" | "done";

export function canTransition(from: TaskStatus, to: TaskStatus): boolean {
  const allowed: Record<TaskStatus, TaskStatus[]> = {
    todo: ["in_progress"],
    in_progress: ["done"],
    done: [],
  };
  return allowed[from].includes(to);
}
```

この関数は I/O に依存しないため、単体テストで薄く守れます（次章以降で扱います）。

## 演習（最小1個）

ランニング例の “最小フォルダ構成” を設計し、責務を書き出してください。

- `domain / usecases / adapters` の 3 区分で開始する
- 境界を跨ぐデータ構造（DTO/型）を 2 つ定義する（例: `CreateTaskInput`, `AssignedTask`）

## よくある失敗

- 複雑性が低いのに層を増やし、デバッグと変更が難しくなる
- UI とドメインロジックの相互参照が増え、テストが困難になる
- 例外・エラー・権限を後回しにし、境界が崩れる

## チェックリスト

- [ ] コアがフレームワークや I/O に依存していない
- [ ] 境界を跨ぐ型/契約が明確
- [ ] UI の状態管理が増殖しない設計になっている

## 前後リンク

- [目次]({{ '/chapters/' | relative_url }})
- [前章: 03. 結合の物差し（S/D/V）]({{ '/chapters/03-coupling-balance-sdv/' | relative_url }})
- [次章: 05. 設計時にテストを織り込む]({{ '/chapters/05-design-for-testability/' | relative_url }})
