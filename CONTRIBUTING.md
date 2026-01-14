# CONTRIBUTING

本リポジトリへのコントリビューション手順です。執筆の一貫性とレビュー容易性を優先します。

## 前提

- 参照書籍・PDF本文などの転載は禁止します（要約・自分の言葉・短い引用に限定）
- 引用/参考文献の扱いは `POLICY.md` を参照してください

## 変更の粒度（推奨）

- 1 PR = 1 目的（例: 1 章の改善、Appendix テンプレの改善、CI 改修）
- 章本文の大規模改訂は、セクション単位で分割してください（レビュー負荷を下げる）

## ブランチ命名（推奨）

- 本文: `content/<topic>`（例: `content/chapter-03-sdv-examples`）
- 運用/テンプレ: `repo/<topic>`（例: `repo/pr-template`）
- CI: `ci/<topic>`（例: `ci/link-check`）
- 修正: `fix/<topic>`（例: `fix/typo-ch02`）

## レビュー観点（必須）

- 章テンプレを満たしているか（`STYLEGUIDE.md`）
- 章間リンク（目次/前後）が壊れていないか
- 「断定の前提（小規模）」が明記されているか
- 引用/参照が `POLICY.md` に適合しているか
- CI が通っているか（導入済みの場合）

## 執筆の方針

- 「判断基準（S/D/V、テスト戦略、非機能の最小合意）」を中心に据える
- フレームワーク固有の実装最適化は原則扱わない（必要なら別 Issue で合意）
- コード例は短くし、境界・依存・型が伝わることを優先する

## book-config.json（シリーズ横展開用メタデータ）

`book-config.json` は、シリーズ書籍の横展開・機械処理（book-formatter）で利用するメタデータです。

- 章/付録の追加・並び替えを行う場合は、以下を同期してください
  - `docs/_data/navigation.yml`（前後ナビの順序）
  - `docs/_includes/sidebar-nav.html`（サイドバーの章/付録表示）
  - `book-config.json`（`structure.chapters` / `structure.appendices`）
- タイトル/説明/著者/バージョンを変更する場合は、`docs/_config.yml` と `book-config.json` の整合も確認してください
