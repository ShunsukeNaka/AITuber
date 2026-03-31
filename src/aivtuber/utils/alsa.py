"""
ALSA エラーメッセージの抑制（WSL2環境向け）

'ALSA lib pcm.c:8772:(snd_pcm_recover) underrun occurred' などの
ノイジーなALSAログをサイレントにする。

使い方:
    from aivtuber.utils.alsa import suppress_alsa_errors
    suppress_alsa_errors()  # sounddevice の import より前に呼ぶ
"""
from __future__ import annotations


def suppress_alsa_errors() -> None:
    """ALSA のエラーハンドラを無効化してログ出力を抑制する"""
    try:
        import ctypes
        from ctypes import CFUNCTYPE, c_char_p, c_int
        asound = ctypes.cdll.LoadLibrary("libasound.so.2")
        asound.snd_lib_error_set_handler(
            CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)(lambda *_: None)
        )
    except OSError:
        pass  # libasound が見つからない環境（macOS等）では何もしない
