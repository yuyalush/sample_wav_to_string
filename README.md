# sample_wav_to_string

WAVファイルを受け取り、Azure AI Speechで文字起こしを行い、正解文章と比較するPythonプログラムです。

## 構成

- `transcribe_compare.py`: 本体CLI
- `requirements.txt`: 依存関係
- `tests/test_compare.py`: 比較ロジックのユニットテスト
- `samples/sample.wav`: サンプルWAV（16kHz/モノラル/16bit）

## 前提条件

1. Python 3.10+（3.9+でも基本動作可）
2. Azure Speechリソース作成済み
3. Speech Key / Region を取得済み

## セットアップ

```bash
cd /tmp/workspace/yuyalush/sample_wav_to_string
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Azure認証情報の設定

環境変数に設定します（推奨）。

```bash
export AZURE_SPEECH_KEY="<your_speech_key>"
export AZURE_SPEECH_REGION="japaneast"
```

> もしくはCLI引数 `--speech-key` / `--speech-region` でも指定できます。

## 実行方法

```bash
python3 transcribe_compare.py <WAVファイルパス> "<正解文章>" [--language ja-JP]
```

例:

```bash
python3 transcribe_compare.py ./samples/sample.wav "テストです" --language ja-JP
```

実行すると以下を出力します。

- 文字起こし結果
- 正解文
- 完全一致（YES/NO）
- 類似度（0〜100%）

## 注意点

- Azure Speechは音声内容に応じて結果が変わるため、比較は「完全一致」と「類似度」の両方を表示します。
- `samples/sample.wav` は動作確認用の音声波形サンプルです。実運用では発話が入ったWAVを使用してください。
- WAVは一般的に **モノラル/16kHz/16bit PCM** を推奨します。

## テスト

```bash
python3 -m unittest -v
```

比較ロジック（正規化・一致判定・類似度算出）を検証します。
