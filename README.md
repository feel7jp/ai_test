# AI Chat (Flask + Gemini / LM Studio)

Flask で動くシンプルなチャットUIです。Google Gemini API と、ローカルの LM Studio を切り替えて利用できます。

## Features
- Web UI からチャット
- Provider 切り替え（Gemini / LM Studio）
- モデル一覧の取得（Gemini / LM Studio）

## Requirements
- Python 3.10+
- Gemini を使う場合: Google API Key
- LM Studio を使う場合: LM Studio のサーバー起動（OpenAI互換）

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables
最低限必要なもの:
- `GEMINI_API_KEY` (Gemini 使用時)

任意:
- `LLM_PROVIDER` (default: `gemini`)
- `GEMINI_MODEL` (default: `models/gemini-2.5-flash`)
- `GEMINI_API_VERSION` (例: `v1`)
- `LMSTUDIO_BASE_URL` (default: `http://localhost:1234/v1`)
- `LMSTUDIO_MODEL` (default: auto)
- `LMSTUDIO_API_KEY` (default: none)
- `LMSTUDIO_TEMPERATURE` (default: `0.7`)
- `MAX_MESSAGE_CHARS` (default: `4000`)
- `MAX_HISTORY` (default: `20`)
- `PORT` (default: `5000`)

`.env` を使う場合はリポジトリに含めないでください。

## Run
```bash
python app.py
```

デバッグ起動:
```bash
python app.py --debug
```

アクセス:
```
http://localhost:5000
```

## Deploy to Vercel
1. Vercel にリポジトリを接続
2. 環境変数（`GEMINI_API_KEY` など）を Vercel の Project Settings で設定
3. Deploy

静的ファイルは `public/static/` に配置しています。Vercel では `public/` 配下が CDN で配信されるため、Flask では静的ファイルをビルドに含めるだけで OK です（ローカル開発時は `/static/*` を Flask が配信します）。
Vercel の Python ランタイムは 3.12 固定です。

## API
- `GET /api/models?provider=gemini|lmstudio`
- `POST /api/chat`  
  body:
  ```json
  {
    "message": "hello",
    "history": [{"role": "user", "content": "hi"}],
    "provider": "gemini",
    "model": "models/gemini-2.5-flash"
  }
  ```

## Notes for public repo
- `.env` や API キーが含まれないことを再確認してください。
- `.venv/` や `__pycache__/` は `.gitignore` 済みです。
