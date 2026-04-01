"""
TTS 再生とアバター制御を統合した speak() 関数。

各スクリプトで重複していた _speak() をここに集約する。
"""
from __future__ import annotations

import asyncio
import io

from ..tts.voicevox import VoicevoxClient
from .base import AvatarController


async def speak(
    tts: VoicevoxClient,
    text: str,
    tts_params: dict,
    avatar: AvatarController,
    emotion_name: str,
) -> None:
    """
    TTS 合成・再生とアバター制御を統合した speak 関数。

    Args:
        tts:          VoicevoxClient（None の場合はアバター制御のみ）
        text:         読み上げテキスト
        tts_params:   synthesize() に渡すパラメータ
        avatar:       AvatarController（NullAvatarController でも可）
        emotion_name: 感情名（"happy", "neutral" など）
    """
    import sounddevice as sd
    import soundfile as sf

    loop = asyncio.get_event_loop()

    try:
        wav = await tts.synthesize(text, **tts_params)
        await avatar.set_emotion(emotion_name)
        data, sr = sf.read(io.BytesIO(wav))
        sd.play(data, sr)

        # sd.wait() をスレッドで実行しつつ、口パクを並行更新
        # _is_playing() だけを終了条件にすると再生が途切れることがある
        play_done = asyncio.Event()

        async def _wait_playback():
            await loop.run_in_executor(None, sd.wait)
            play_done.set()

        playback_task = asyncio.create_task(_wait_playback())
        while not play_done.is_set():
            await avatar.set_mouth_open(0.8)
            await asyncio.sleep(0.05)
        await playback_task
    except Exception as e:
        print(f"\n[TTS エラー: {e}]")
    finally:
        await avatar.set_mouth_open(0.0)
