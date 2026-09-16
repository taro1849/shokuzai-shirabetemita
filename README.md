# 食材調べてみた

身近な食材をひとつずつ深掘りして調べるブログ。Hugo + GitHub Pages で運用。

## 開発

```bash
hugo server --buildDrafts
```

## 新しい記事を書く

```bash
hugo new content posts/記事名.md
```

`blog_guide.md` の方針に沿って執筆し、公開前に `draft: true` を `false` に変更する。

## 公開

`main` ブランチに push すると GitHub Actions が自動でビルド・GitHub Pages への反映を行う（下書き記事は公開ビルドに含まれない）。
