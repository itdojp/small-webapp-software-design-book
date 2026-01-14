# 要件から始めるソフトウェア設計（小規模TS Webアプリの実践）

小〜中規模の Web フロントエンドを持つシステム（TypeScript 想定）を対象に、要件定義→設計→テストまでを一貫した判断基準で進めるための実践教材です。

## 公開（GitHub Pages）

- URL: https://itdojp.github.io/small-webapp-software-design-book/
- 設定: Repo Settings → Pages → Deploy from a branch → `main` / `/docs`

## ローカルプレビュー（Jekyll）

前提: Ruby + Bundler が利用できる環境

- `bundle install`
- `bundle exec jekyll serve --source docs --config docs/_config.yml --baseurl ""`
- ブラウザで `http://127.0.0.1:4000/` を開く

## CI（品質ゲート）

- `.github/workflows/ci.yml` で以下を実行します
  - Jekyll build（`bundle exec jekyll build --source docs --config docs/_config.yml`）
  - Markdown lint（markdownlint）
  - リンクチェック（内部: `scripts/check_internal_links.py` / 外部: lychee）

## 読み方

- GitHub Pages（公開後）: https://itdojp.github.io/small-webapp-software-design-book/
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
- 商用利用等の相談は `knowledge@itdo.jp` まで連絡してください

## 注意事項

- 参照書籍・PDF本文などの転載物はコミットしません
