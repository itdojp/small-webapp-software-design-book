# TypeScript本文例fixture

第4・5章で「実行可能例」と表示するTypeScript/Vitestコードの検証用fixtureです。完成アプリケーションではなく、本文に掲載する最小例だけを管理します。

## 固定環境

2026-07-20 JSTに次の公式情報とpackage metadataを確認し、patch versionを固定しています。

- Node.js 24.18.0 (LTS): <https://nodejs.org/en/blog/release/v24.18.0>
- TypeScript 7.0.2: <https://www.npmjs.com/package/typescript/v/7.0.2>
- Vitest 4.1.10: <https://www.npmjs.com/package/vitest/v/4.1.10>

Node.js/npmのversion不一致は`.npmrc`の`engine-strict=true`で拒否します。依存ツリーは`package-lock.json`を正本とし、installにはlifecycle scriptを実行しない`npm ci --ignore-scripts`を使用します。

## 検証

repository rootで次を実行します。

```bash
python3 scripts/check_typescript_examples.py
python3 scripts/check_typescript_examples.py --self-test
npm ci --prefix examples/typescript --ignore-scripts
npm run typecheck --prefix examples/typescript
npm test --prefix examples/typescript
npm audit --prefix examples/typescript --audit-level=moderate
```

同期checkerは、本文のTypeScript系コードフェンスとfixtureの完全一致を検査します。fixture pathには`chapter-04`または`chapter-05`を含めるため、型エラーは章とfixture、テスト失敗は章・test file・test name、同期不一致は章ファイル・fence開始行・fixture pathから追跡できます。

## 本文例を変更する場合

1. `examples/typescript/src/`のfixtureを変更する。
2. 対応する本文fenceを同じ内容へ更新する。
3. 読者向けの分類表示と直後の`code-example` markerを維持する。
4. 上記の同期検査、型検査、テストを実行する。

抜粋は`分類: 抜粋`、実行を意図しないアルゴリズム記述は`分類: 疑似コード`と表示します。これらにはfixture pathを付けません。分類のないTypeScript系fenceはCIで拒否します。

`npm audit`はmoderate以上をCI failureとします。low severityが検出された場合も出力を確認し、影響、対応要否、再確認条件をIssueまたはPRへ記録します。
