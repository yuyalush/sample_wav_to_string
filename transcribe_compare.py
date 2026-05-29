#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class ComparisonResult:
    transcription: str
    expected: str
    exact_match: bool
    similarity: float


def normalize_text(text: str) -> str:
    return "".join(text.split()).lower()


def compare_texts(transcription: str, expected: str) -> ComparisonResult:
    normalized_transcription = normalize_text(transcription)
    normalized_expected = normalize_text(expected)
    similarity = SequenceMatcher(None, normalized_transcription, normalized_expected).ratio() * 100
    return ComparisonResult(
        transcription=transcription,
        expected=expected,
        exact_match=normalized_transcription == normalized_expected,
        similarity=similarity,
    )


def transcribe_wav(
    wav_path: str,
    speech_key: str,
    speech_region: str,
    language: str,
) -> str:
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError as exc:
        raise RuntimeError(
            "azure-cognitiveservices-speech が未インストールです。READMEの手順でインストールしてください。"
        ) from exc

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = language

    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text.strip()

    if result.reason == speechsdk.ResultReason.NoMatch:
        raise RuntimeError("音声を認識できませんでした。WAVファイル内容を確認してください。")

    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        message = f"認識がキャンセルされました: reason={cancellation_details.reason}"
        if cancellation_details.error_details:
            message += f", detail={cancellation_details.error_details}"
        raise RuntimeError(message)

    raise RuntimeError("不明なエラーが発生しました。")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WAVを文字起こしして正解文と比較します")
    parser.add_argument("wav", help="入力WAVファイルへのパス")
    parser.add_argument("expected", help="正解文")
    parser.add_argument("--language", default="ja-JP", help="認識言語 (既定: ja-JP)")
    parser.add_argument("--speech-key", default=os.getenv("AZURE_SPEECH_KEY"), help="Azure Speechキー")
    parser.add_argument(
        "--speech-region",
        default=os.getenv("AZURE_SPEECH_REGION"),
        help="Azure Speechリージョン (例: japaneast)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if not os.path.exists(args.wav):
        print(f"エラー: WAVファイルが見つかりません: {args.wav}", file=sys.stderr)
        return 2

    if not args.speech_key or not args.speech_region:
        print(
            "エラー: Azure資格情報が未設定です。--speech-key/--speech-region もしくは環境変数を指定してください。",
            file=sys.stderr,
        )
        return 2

    try:
        transcription = transcribe_wav(
            wav_path=args.wav,
            speech_key=args.speech_key,
            speech_region=args.speech_region,
            language=args.language,
        )
        result = compare_texts(transcription, args.expected)
    except RuntimeError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    print("=== 文字起こし結果 ===")
    print(result.transcription)
    print("=== 比較結果 ===")
    print(f"正解文      : {result.expected}")
    print(f"完全一致    : {'YES' if result.exact_match else 'NO'}")
    print(f"類似度(%)   : {result.similarity:.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
