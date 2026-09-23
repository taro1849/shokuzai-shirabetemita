"""
記事に挿入する画像をGemini API (gemini-2.5-flash-image) で生成するスクリプト。

使い方:
    python scripts/generate_images.py <slug>

<slug> に対応する scripts/image_prompts/<slug>.json を読み込み、
各エントリの prompt で画像を生成して static/images/posts/<slug>/ に保存する。

image_prompts/<slug>.json の形式:
[
  {"file": "01-history.jpg", "prompt": "..."},
  {"file": "02-nutrition.jpg", "prompt": "..."}
]

APIキーはプロジェクト直下の .env ファイル (GEMINI_API_KEY=...) から読み込む。
"""

import base64
import json
import os
import sys
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = "gemini-2.5-flash-image"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def load_api_key():
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        sys.exit(f".envが見つかりません: {env_path}")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit(".envにGEMINI_API_KEYがありません")


def generate_image(api_key, prompt, out_path):
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"APIエラー ({e.code}): {detail}") from e

    parts = data["candidates"][0]["content"]["parts"]
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline:
            img_bytes = base64.b64decode(inline["data"])
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            return True

    raise RuntimeError(f"画像データが応答に含まれていません: {json.dumps(data, ensure_ascii=False)[:500]}")


def main():
    if len(sys.argv) != 2:
        print("使い方: python scripts/generate_images.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    prompts_path = os.path.join(ROOT, "scripts", "image_prompts", f"{slug}.json")
    if not os.path.exists(prompts_path):
        sys.exit(f"プロンプトファイルが見つかりません: {prompts_path}")

    with open(prompts_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    api_key = load_api_key()
    out_dir = os.path.join(ROOT, "static", "images", "posts", slug)

    for entry in entries:
        out_path = os.path.join(out_dir, entry["file"])
        print(f"生成中: {entry['file']} ...")
        generate_image(api_key, entry["prompt"], out_path)
        print(f"  -> 保存しました: {out_path}")

    print("完了しました。")


if __name__ == "__main__":
    main()
