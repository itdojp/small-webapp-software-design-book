## 変更内容

-

## 対象 Issue

- Closes #

## チェックリスト（必須）

- [ ] `STYLEGUIDE.md` の章テンプレ/見出しルールに適合している
- [ ] 章間リンク（目次/前へ/次へ）が壊れていない
- [ ] 引用/参考文献の扱いが `POLICY.md` に適合している（転載なし、引用最小）
- [ ] CI が通っている（導入済みの場合）

- [ ] Book QA（Unicode / textlint(PRH) / 内部リンク・アンカー / Jekyll build / built-site smoke）: PASS
  - 実行URL: （GitHub Actions の workflow run URL）

- [ ] Pages確認（原則必須）
  - 確認URL: https://itdojp.github.io/small-webapp-software-design-book/ （fork/rename の場合は適宜読み替え）
  - [ ] トップページ HTTP 200
  - [ ] 主要導線（navigation.yml 相当）で 404 が無い
  - [ ] 表示崩れが無い（図表/表/コード中心）

## Review Completion Gate

- [ ] GitHub Copilot review を依頼した（必要な場合）
- [ ] review 本文、inline comment、suggestion を全件確認した
- [ ] 必要な修正、または変更不要の理由を返信した
- [ ] 未解決 review thread が 0 件である

## 証跡（該当する場合）

- 仕様/設計差分:
- テスト/eval/benchmark 実行結果:
- 形式仕様・不変条件・反例確認:
- AI 利用時の投入禁止データ確認:
- CI / Pages / main checks:

## 補足（レビュー観点）

- 断定している箇所の前提（小規模/TS/Web）が明確か
- 判断基準（S/D/V、非機能の最小合意、テスト配分）に接続しているか
