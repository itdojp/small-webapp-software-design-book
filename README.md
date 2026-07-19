# 要件から始めるソフトウェア設計（小規模TS Webアプリの実践）

小〜中規模の Web フロントエンドを持つシステム（TypeScript 想定）を対象に、要件定義→設計→テストまでを一貫した判断基準で進めるための実践教材です。

## 公開（GitHub Pages）

- URL: [要件から始めるソフトウェア設計（小規模TS Webアプリの実践）](https://itdojp.github.io/small-webapp-software-design-book/)
- 設定: Repo Settings → Pages → Deploy from a branch → `main` / `/docs`

## ローカルプレビュー（Jekyll）

前提: Ruby + Bundler が利用できる環境

- `bundle install`
- `bundle exec jekyll serve --source docs --config docs/_config.yml --baseurl ""`
- ブラウザで `http://127.0.0.1:4000/` を開く

## TypeScript本文例の検証

第4・5章で「実行可能例」と表示するコードは、`examples/typescript/`のfixtureと同期し、CIで型検査・Vitestを実行します。固定環境はNode.js 24.18.0、TypeScript 7.0.2、Vitest 4.1.10です。

- `python3 scripts/check_typescript_examples.py && python3 scripts/check_typescript_examples.py --self-test`
- `npm ci --prefix examples/typescript --ignore-scripts`
- `npm run typecheck --prefix examples/typescript`
- `npm test --prefix examples/typescript`
- 詳細: [`examples/typescript/README.md`](examples/typescript/README.md)

## CI（品質ゲート）

ローカルで最小確認を行う場合は、次を実行します。

- `python3 scripts/check_book_config_navigation_consistency.py`
- `python3 scripts/check_internal_links.py`
- `python3 scripts/check_auth_session_contract.py && python3 scripts/check_auth_session_contract.py --self-test`
- `python3 scripts/check_typescript_examples.py && python3 scripts/check_typescript_examples.py --self-test`
- `bundle exec jekyll build --source docs --config docs/_config.yml --destination _site`

CIでは以下を実行します。

- Jekyll build（`bundle exec jekyll build --source docs --config docs/_config.yml`）
- Markdown lint（markdownlint）
- メタデータ/ナビゲーション整合性チェック（`scripts/check_book_config_navigation_consistency.py`）
- 認証・セッション文書の必須marker・整合行と負例の回帰チェック（`scripts/check_auth_session_contract.py`）
- TypeScript本文例の分類・fixture同期・型検査・Vitest（独立workflow: `.github/workflows/typescript-examples.yml`）
- リンクチェック（内部: `scripts/check_internal_links.py` / 外部: lychee）

## 読み方

- GitHub Pages（公開後）: [公開トップページ](https://itdojp.github.io/small-webapp-software-design-book/)
- リポジトリ内: `docs/index.md` → `docs/chapters/TOC.md` → 各章 → `docs/appendix/`

## ディレクトリ構成（概要）

- `book-config.json`: シリーズ横展開/機械処理向けのメタデータ（book-formatter 用）
- `docs/index.md`: トップページ
- `docs/chapters/`: 章（`TOC.md` を含む）
- `docs/appendix/`: 付録（チェックリスト、テンプレ、参考文献）
- `docs/_layouts/`, `docs/_includes/`, `docs/assets/`: GitHub Pages（Jekyll）用

## コントリビューション

- 章構成・表現の改善は Issue / PR で提案してください
- 執筆ルールは `STYLEGUIDE.md` を参照してください

## ライセンス

- `LICENSE.md` を参照してください（CC BY-NC-SA 4.0）
- 商用利用等の相談は [knowledge@itdo.jp](mailto:knowledge@itdo.jp) まで連絡してください

## 注意事項

- 参照書籍・PDF本文などの転載物はコミットしません
