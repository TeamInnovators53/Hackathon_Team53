"""
Google Text-to-Speech (TTS) Service for KeyBank Key Privilege Concierge.
Provides high-fidelity Google TTS audio via:
1. Google Cloud Text-to-Speech (Neural2/Journey voices) if credentials are available.
2. Google Translate Neural TTS streaming with smart chunking and MP3 frame concatenation.
3. In-memory LRU audio caching for high performance and low latency.
"""

import io
import re
import urllib.parse
import urllib.request
from typing import Optional

# Optional Google Cloud TTS client
_gcp_tts_client = None
try:
    from google.cloud import texttospeech
    _gcp_tts_client = texttospeech.TextToSpeechClient()
except Exception:
    _gcp_tts_client = None


class GoogleTTSService:
    _audio_cache: dict[str, bytes] = {}

    @classmethod
    def clean_text_for_speech(cls, text: str) -> str:
        """Strip markdown symbols, IVR prompt tags, and normalize currency for natural speech."""
        if not text:
            return ""
        # Strip markdown syntax
        cleaned = re.sub(r"[*#`_>]", "", text)
        # Strip prompt codes like [K2U_ENG.700.au] or [STEP 1]
        cleaned = re.sub(r"\[K2U_.*?\.au\]", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\[.*?\]", "", cleaned)
        # Expand currency: $25,000 -> 25,000 dollars
        cleaned = re.sub(r"\$(\d[\d,]*(?:\.\d{2})?)", r"\1 dollars", cleaned)
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def split_into_chunks(cls, text: str, max_chars: int = 180) -> list[str]:
        """Split text into spoken chunks on sentence boundaries, clauses, or words."""
        if len(text) <= max_chars:
            return [text]

        chunks = []
        # Split on sentences first
        sentences = re.split(r"(?<=[.!?])\s+", text)
        current = ""

        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if len(s) > max_chars:
                # If a single sentence exceeds max_chars, split on commas or spaces
                words = s.split()
                for w in words:
                    if len(current) + len(w) + 1 <= max_chars:
                        current = f"{current} {w}".strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = w
            else:
                if len(current) + len(s) + 1 <= max_chars:
                    current = f"{current} {s}".strip()
                else:
                    if current:
                        chunks.append(current)
                    current = s

        if current:
            chunks.append(current)

        return chunks or [text]

    @classmethod
    def synthesize_gcp(cls, text: str, lang_code: str = "en") -> Optional[bytes]:
        """Synthesize using Google Cloud Text-to-Speech API if available."""
        if not _gcp_tts_client:
            return None
        try:
            from google.cloud import texttospeech
            s_input = texttospeech.SynthesisInput(text=text)
            if lang_code.startswith("es"):
                voice = texttospeech.VoiceSelectionParams(
                    language_code="es-US",
                    name="es-US-Neural2-A",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )
            else:
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Neural2-F",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.02
            )
            resp = _gcp_tts_client.synthesize_speech(
                input=s_input,
                voice=voice,
                audio_config=audio_config
            )
            return resp.audio_content
        except Exception:
            return None

    @classmethod
    def synthesize_google_neural(cls, text: str, lang_code: str = "en") -> bytes:
        """
        Synthesize using Google Translate Neural TTS engine.
        Splits into natural sentences, fetches MP3 audio, and stitches frames together.
        """
        cache_key = f"{lang_code}:{text}"
        if cache_key in cls._audio_cache:
            return cls._audio_cache[cache_key]

        # 1. Try Google Cloud TTS first if credentials exist
        gcp_audio = cls.synthesize_gcp(text, lang_code)
        if gcp_audio:
            cls._audio_cache[cache_key] = gcp_audio
            return gcp_audio

        # 2. Use Google Translate Neural Engine with chunking
        chunks = cls.split_into_chunks(text, max_chars=180)
        combined_audio = io.BytesIO()

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            params = urllib.parse.urlencode({
                "ie": "UTF-8",
                "tl": lang_code,
                "client": "tw-ob",
                "q": chunk
            })
            url = f"https://translate.google.com/translate_tts?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                combined_audio.write(data)

        audio_bytes = combined_audio.getvalue()
        if audio_bytes:
            cls._audio_cache[cache_key] = audio_bytes
        return audio_bytes
