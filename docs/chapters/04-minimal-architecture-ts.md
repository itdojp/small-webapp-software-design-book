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
- 状態は必要最小限にし、コアに押し込めない（コアは **I/O やグローバルな外部状態** に依存しない。状態は引数で受け、戻り値で返す）
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

### 境界を跨ぐ型（DTO）の最小ルール

小規模でも、境界を跨ぐデータ（DTO）を先に決めると、UI/API/DB の相互作用が増えにくくなります。

- domain の型（エンティティ/値）は、外部I/F（HTTP/DB）の都合に引きずられない
- adapters で扱う入出力（JSON/SQL）は、usecases の DTO に変換して渡す
- UI は「usecases が返す DTO」だけを前提にし、domain の内部構造を前提にしない

例（割り当てユースケースの DTO）:

```ts
export type AssignTaskInput = { taskId: string; assigneeId: string };
export type AssignTaskOutput = {
  taskId: string;
  assigneeId: string;
  assignedAt: string; // RFC3339（例: "2026-02-18T12:34:56Z" or "2026-02-18T21:34:56+09:00"）
};
```

DTO に「観測できる結果」だけを載せると、後から内部構造を変えても UI/API が壊れにくくなります。

#### 日時/タイムゾーンの最小方針（DTO・計算の落とし穴）

- 外部I/F（JSON）は **RFC3339** 文字列で統一し、`Z`（UTC）または固定オフセット（例: `+09:00`）のどちらを採用するかを先に決める
- 「1日」を `24*60*60*1000` のような秒数で扱うか、「暦日（カレンダー日）」で扱うかを要件として固定する（締切/期限は暦日で定義されることが多い）
- UI と API のどちらが「表示用のタイムゾーン変換」を担うかを決め、二重変換やローカル時刻の混入を避ける

### エラーの扱い（境界で整形する）

例外やエラーは、domain/usecases 内で「理由」を保持し、外部へ出す境界（例: HTTP）で形式を揃えます。

- domain: ルール違反（権限、状態遷移、制約）を「理由付き」で返す
- usecases: domain の理由を、外部I/Fの失敗（通知失敗等）と区別して扱う
- adapters: 失敗理由をステータスコード/エラー形式に写像し、クライアントへ返す

例（エラーをコード化する最小形式）:

```ts
export type UsecaseError =
  | { code: "forbidden"; message: string }
  | { code: "not_found"; message: string }
  | { code: "conflict"; message: string }
  | { code: "invalid"; message: string };
```

この「code」の集合が、仕様（Behavior）とテストの契約になります。

成果物として残す場合:

- エラーコードカタログ（任意）: [Appendix B: テンプレ集（B-10）]({{ '/appendix/B-templates/' | relative_url }})
- 記入例: [Appendix D: 記入例（D-18）]({{ '/appendix/D-samples/' | relative_url }})
- API 契約（任意）: [Appendix B: テンプレ集（B-14）]({{ '/appendix/B-templates/' | relative_url }})
- 記入例: [Appendix D: 記入例（D-22）]({{ '/appendix/D-samples/' | relative_url }})
- データ整合性/同時更新（任意）: [Appendix B: テンプレ集（B-15）]({{ '/appendix/B-templates/' | relative_url }})
- 記入例: [Appendix D: 記入例（D-23）]({{ '/appendix/D-samples/' | relative_url }})

### 依存方向のルール（禁止事項で固定する）

小規模では「層」を増やすより、禁止事項を明文化して逸脱を検知できる状態にするほうが有効です。

- domain は adapters を import しない（HTTP/DB/外部通知/環境変数に依存しない）
- usecases は具体実装（DB クライアント等）に依存しない（port を引数で受ける）
- adapters は domain/usecases を呼ぶが、その逆はしない（依存を逆流させない）
- UI は domain を直接参照しない（usecases の DTO とエラー形式を契約にする）

補足（UI ↔ domain 境界の判断材料）:

- 参照を避けたい例: UI が domain の内部ルール（状態遷移/期限判定/権限判定）を直接呼び出し、API と二重実装になる
- 許容しやすい例: UI と API で共有する **契約（DTO/エラーコード/列挙型）** を `contracts/` 等に切り出して参照する（domain ロジックは含めない）
- shared 肥大化の防止: `contracts/` は「境界を跨ぐデータと識別子のみ」とし、ビジネスロジック/フレームワーク依存を置かない（増やす場合はレビュー対象にする）

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
- [ ] エラー理由が境界で整形され、仕様とテストで検証できる
- [ ] UI の状態管理が増殖しない設計になっている
