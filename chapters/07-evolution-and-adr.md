---
title: "07. 進化条件（ADRと境界の強化タイミング）"
permalink: /chapters/07-evolution-and-adr/
show_nav: true
prev: /chapters/06-test-strategy-pyramid/
next: /appendix/A-checklists/
---

# 07. 進化条件（ADRと境界の強化タイミング）

## 目的

- 「いつ境界を強めるか」を、観測可能な条件（S/D/V の悪化、運用要件）で判断できるようにする
- ADR を最小限に運用し、意思決定の再現性と合意形成の速度を上げる

## 前提/用語

- **ADR**: Architecture Decision Record（意思決定の記録）
- **進化条件**: 現状の設計が限界に近づいた兆候（変更の痛み、障害、運用負債）

## 要点

- 境界の強化は、コストに見合うトリガーが発生したときに行う（先回りしない）
- S/D/V の悪化は「結合の偏り」の兆候。トップ依存の再採点で把握する
- ADR は長文ではなく、**Context / Decision / Consequences** の最小記録でよい

## 演習（最小1個）

次の状況を想定し、ADR を 1 つ作成してください。

- 状況: 権限モデルが拡張され、UI と API の条件分岐が急増した
- 目的: 変更容易性とテスト容易性を確保したい

テンプレは Appendix B を利用してください。

## よくある失敗

- ADR が議事録化し、意思決定の要点が埋もれる
- 進化の根拠が「気分」になり、境界強化が目的化する
- 変更の痛みを可視化しないまま、部分最適なリファクタリングを繰り返す

## チェックリスト

- [ ] 境界強化のトリガーが明確（S/D/V、運用要件、変更頻度）
- [ ] ADR の粒度が一定で、検索・再利用できる
- [ ] 設計変更がテスト戦略（配分）に反映されている

## 前後リンク

- [目次]({{ '/chapters/' | relative_url }})
- [前章: 06. テスト戦略（単体/統合/E2E）]({{ '/chapters/06-test-strategy-pyramid/' | relative_url }})
- [次: Appendix A]({{ '/appendix/A-checklists/' | relative_url }})
