"""ElevenLabs text-to-speech with an on-disk cache.

The API key is read from the ELEVENLABS_API_KEY environment variable (or the
file named by ELEVENLABS_API_KEY_FILE). It is never written into the repo.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "media" / "voice_cache"

# "Chris - Charming, Down-to-Earth": warm, curious, conversational narrator.
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "iP95p4xoKVk53GoZ742B")
MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
VOICE_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.75,
    "style": 0.15,
    "use_speaker_boost": True,
    "speed": 1.1,
}


def _api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key and os.environ.get("ELEVENLABS_API_KEY_FILE"):
        key = Path(os.environ["ELEVENLABS_API_KEY_FILE"]).read_text().strip()
    if not key:
        raise RuntimeError(
            "Set ELEVENLABS_API_KEY (or ELEVENLABS_API_KEY_FILE) to synthesize narration."
        )
    return key


def audio_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ]
    )
    return float(out.strip())


def _cache_key(text: str) -> str:
    blob = json.dumps(
        {"t": text, "v": VOICE_ID, "m": MODEL_ID, "s": VOICE_SETTINGS}, sort_keys=True
    )
    return hashlib.sha1(blob.encode()).hexdigest()[:16]


def synthesize(text: str, previous_text: str | None = None) -> tuple[Path, float]:
    """Return (path_to_mp3, duration_seconds) for ``text``, using the cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_cache_key(text)}.mp3"
    if not path.exists():
        body = {
            "text": text,
            "model_id": MODEL_ID,
            "voice_settings": VOICE_SETTINGS,
        }
        if previous_text:
            body["previous_text"] = previous_text
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            "?output_format=mp3_44100_128",
            data=json.dumps(body).encode(),
            headers={
                "xi-api-key": _api_key(),
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )
        last_err = None
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                tmp = path.with_suffix(".part")
                tmp.write_bytes(data)
                tmp.rename(path)
                break
            except (urllib.error.URLError, TimeoutError) as err:  # retry w/ backoff
                last_err = err
                time.sleep(2 ** (attempt + 1))
        else:
            raise RuntimeError(f"TTS failed for {text[:60]!r}: {last_err}")
    return path, audio_duration(path)
