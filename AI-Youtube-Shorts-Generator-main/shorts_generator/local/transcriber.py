"""Local/API transcription support.

Supports:
- local = faster-whisper
- gemini = Gemini video transcription

Returns the same shape the highlight generator expects:
{
    "duration": float,
    "segments": [
        {
            "start": float,
            "end": float,
            "text": str
        }
    ]
}
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, Optional

from ..config import (
    LOCAL_OUTPUT_DIR,
    LOCAL_WHISPER_DEVICE,
    LOCAL_WHISPER_MODEL,
    TRANSCRIPTION_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)


# ---------------------------------------------------------------------------
# SRT CACHE
# ---------------------------------------------------------------------------

def _transcript_cache_path(media_path: str) -> Path:
    """Return the .srt cache path for a media file."""
    cache_dir = Path(LOCAL_OUTPUT_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / (Path(media_path).stem + ".srt")


def _format_srt_timestamp(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))

    ms = total_ms % 1000
    total_s = total_ms // 1000

    s = total_s % 60
    total_m = total_s // 60

    m = total_m % 60
    h = total_m // 60

    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _parse_srt_timestamp(value: str) -> float:
    match = re.fullmatch(
        r"(\d{2}):(\d{2}):(\d{2}),(\d{3})",
        value.strip(),
    )

    if not match:
        raise ValueError(f"Invalid SRT timestamp: {value!r}")

    hours, minutes, seconds, millis = map(int, match.groups())

    return (
        hours * 3600
        + minutes * 60
        + seconds
        + millis / 1000.0
    )


def _write_srt_cache(media_path: str, transcript: Dict) -> Path:
    cache_path = _transcript_cache_path(media_path)

    lines = []

    for idx, segment in enumerate(
        transcript.get("segments", []),
        start=1,
    ):
        start = _format_srt_timestamp(
            float(segment["start"])
        )

        end = _format_srt_timestamp(
            float(segment["end"])
        )

        text = (
            str(segment.get("text", ""))
            .strip()
            .replace("\r", "")
            .replace("\n", " ")
        )

        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")

    cache_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return cache_path


def _load_srt_cache(cache_path: Path) -> Dict:
    content = cache_path.read_text(
        encoding="utf-8-sig"
    ).strip()

    if not content:
        return {
            "duration": 0.0,
            "segments": [],
        }

    segments = []

    for block in re.split(
        r"\n\s*\n",
        content,
    ):
        lines = [
            line.strip("\ufeff")
            for line in block.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        # Handle SRT sequence number.
        if (
            "-->" not in lines[0]
            and len(lines) > 1
            and "-->" in lines[1]
        ):
            lines = lines[1:]

        if not lines or "-->" not in lines[0]:
            continue

        start_raw, end_raw = [
            part.strip()
            for part in lines[0].split(
                "-->",
                1,
            )
        ]

        text = "\n".join(lines[1:]).strip()

        segments.append(
            {
                "start": _parse_srt_timestamp(start_raw),
                "end": _parse_srt_timestamp(end_raw),
                "text": text,
            }
        )

    duration = (
        segments[-1]["end"]
        if segments
        else 0.0
    )

    return {
        "duration": duration,
        "segments": segments,
    }


# ---------------------------------------------------------------------------
# DEVICE
# ---------------------------------------------------------------------------

def _resolve_device() -> str:
    if LOCAL_WHISPER_DEVICE != "auto":
        return LOCAL_WHISPER_DEVICE

    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            # Test that CUDA actually works.
            torch.zeros(
                1,
                device="cuda",
            )

            return "cuda"

    except (
        ImportError,
        OSError,
        RuntimeError,
    ):
        pass

    return "cpu"


# ---------------------------------------------------------------------------
# GEMINI TRANSCRIPTION
# ---------------------------------------------------------------------------

def _transcribe_gemini(
    media_path: str,
    language: Optional[str] = None,
) -> Dict:
    """Transcribe a video using Gemini."""

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file."
        )

    try:
        from google import genai
    except ImportError as e:
        raise RuntimeError(
            "google-genai is required for Gemini transcription. "
            "Install it with:\n"
            "pip install google-genai"
        ) from e

    print(
        "[transcribe/gemini] Creating Gemini client...",
        flush=True,
    )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    print(
        f"[transcribe/gemini] Uploading video: {media_path}",
        flush=True,
    )

    uploaded_file = client.files.upload(
        file=media_path
    )

    print(
        f"[transcribe/gemini] Uploaded file: "
        f"{uploaded_file.name}",
        flush=True,
    )

    # Gemini needs the uploaded video to become ACTIVE
    # before it can be used for inference.
    while (
        not uploaded_file.state
        or uploaded_file.state.name != "ACTIVE"
    ):
        state_name = (
            uploaded_file.state.name
            if uploaded_file.state
            else "UNKNOWN"
        )

        print(
            f"[transcribe/gemini] "
            f"Video processing... state={state_name}",
            flush=True,
        )

        if state_name == "FAILED":
            error_message = getattr(
                uploaded_file,
                "error",
                None,
            )

            raise RuntimeError(
                "Gemini failed to process the video: "
                f"{error_message}"
            )

        time.sleep(3)

        uploaded_file = client.files.get(
            name=uploaded_file.name
        )

    print(
        "[transcribe/gemini] Video is ACTIVE.",
        flush=True,
    )

    language_instruction = (
        f"Use {language} language."
        if language
        else "Automatically detect the spoken language."
    )

    prompt = f"""
Transcribe the spoken audio in this video.

{language_instruction}

This is for an automated short-video editing pipeline.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "segments": [
    {{
      "start": 0.0,
      "end": 4.2,
      "text": "spoken words here"
    }}
  ]
}}

Rules:

1. Use seconds for start and end.
2. Start and end must be numbers.
3. Keep segments reasonably short.
4. Preserve the actual spoken words.
5. Do not summarize.
6. Do not describe the visuals.
7. Do not add commentary.
8. Do not use Markdown code fences.
9. Include all spoken content.
10. Keep the timestamps in chronological order.

Return only the JSON object.
"""

    print(
        "[transcribe/gemini] Requesting timestamped transcript...",
        flush=True,
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            uploaded_file,
            prompt,
        ],
    )

    raw_text = (
        response.text or ""
    ).strip()

    if not raw_text:
        raise RuntimeError(
            "Gemini returned an empty transcription."
        )

    print(
        "[transcribe/gemini] Gemini response received.",
        flush=True,
    )

    # Remove accidental Markdown fences if Gemini adds them.
    raw_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        raw_text,
        flags=re.IGNORECASE,
    )

    raw_text = re.sub(
        r"\s*```$",
        "",
        raw_text,
    )

    raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(
            "[transcribe/gemini] Raw response:",
            raw_text[:2000],
            flush=True,
        )

        raise RuntimeError(
            "Gemini returned invalid JSON for the transcript."
        ) from e

    raw_segments = data.get(
        "segments",
        [],
    )

    segments = []

    for item in raw_segments:
        try:
            start = float(item["start"])
            end = float(item["end"])
            text = str(
                item.get("text", "")
            ).strip()
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            continue

        if end <= start:
            continue

        if not text:
            continue

        segments.append(
            {
                "start": start,
                "end": end,
                "text": text,
            }
        )

    if not segments:
        raise RuntimeError(
            "Gemini returned no usable transcript segments."
        )

    segments.sort(
        key=lambda x: x["start"]
    )

    duration = segments[-1]["end"]

    # Gemini may expose video duration in metadata.
    try:
        video_metadata = getattr(
            uploaded_file,
            "video_metadata",
            None,
        )

        video_duration = getattr(
            video_metadata,
            "video_duration",
            None,
        )

        if video_duration:
            duration_text = str(
                video_duration
            ).rstrip("s")

            duration = max(
                duration,
                float(duration_text),
            )

    except (
        TypeError,
        ValueError,
    ):
        pass

    transcript = {
        "duration": float(duration),
        "segments": segments,
    }

    print(
        f"[transcribe/gemini] "
        f"{len(segments)} segments, "
        f"{duration:.1f}s of audio",
        flush=True,
    )

    return transcript


# ---------------------------------------------------------------------------
# LOCAL WHISPER TRANSCRIPTION
# ---------------------------------------------------------------------------

def _transcribe_whisper(
    media_path: str,
    language: Optional[str] = None,
) -> Dict:
    """Transcribe using local faster-whisper."""

    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError(
            "faster-whisper is required for local transcription. "
            "Install it with:\n"
            "pip install -r requirements-local.txt"
        ) from e

    device = _resolve_device()

    compute_type = (
        "float16"
        if device == "cuda"
        else "int8"
    )

    print(
        f"[transcribe/local] "
        f"faster-whisper "
        f"model={LOCAL_WHISPER_MODEL} "
        f"device={device}",
        flush=True,
    )

    from ..config import (
        LOCAL_WHISPER_VAD_FILTER,
        LOCAL_WHISPER_VAD_PARAMETERS,
    )

    print(
        "[transcribe/local] STEP A: "
        "Loading Whisper model...",
        flush=True,
    )

    model = WhisperModel(
        LOCAL_WHISPER_MODEL,
        device=device,
        compute_type=compute_type,
    )

    print(
        "[transcribe/local] STEP B: "
        "Whisper model loaded successfully",
        flush=True,
    )

    transcribe_kwargs = {
        "audio": media_path,
        "language": language,
        "beam_size": 5,
        "condition_on_previous_text": False,
    }

    if LOCAL_WHISPER_VAD_FILTER:
        transcribe_kwargs["vad_filter"] = True
        transcribe_kwargs[
            "vad_parameters"
        ] = LOCAL_WHISPER_VAD_PARAMETERS
    else:
        transcribe_kwargs[
            "vad_filter"
        ] = False

    print(
        "[transcribe/local] STEP C: "
        "Starting transcription...",
        flush=True,
    )

    segments_iter, info = model.transcribe(
        **transcribe_kwargs
    )

    print(
        "[transcribe/local] STEP D: "
        "Transcription iterator created",
        flush=True,
    )

    segments = []

    print(
        "[transcribe/local] STEP E: "
        "Reading transcription segments...",
        flush=True,
    )

    for s in segments_iter:
        segment = {
            "start": float(s.start),
            "end": float(s.end),
            "text": (s.text or "").strip(),
        }

        segments.append(segment)

        print(
            f"[transcribe/local] segment: "
            f"{segment['start']:.1f}s -> "
            f"{segment['end']:.1f}s",
            flush=True,
        )

    duration = float(
        getattr(info, "duration", 0.0)
    ) or (
        segments[-1]["end"]
        if segments
        else 0.0
    )

    print(
        f"[transcribe/local] STEP F: "
        f"{len(segments)} segments, "
        f"{duration:.0f}s of audio",
        flush=True,
    )

    return {
        "duration": duration,
        "segments": segments,
    }


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def transcribe_local(
    media_path: str,
    language: Optional[str] = None,
) -> Dict:
    """Transcribe media using the configured provider."""

    cache_path = _transcript_cache_path(
        media_path
    )

    # -------------------------------------------------------
    # CACHE
    # -------------------------------------------------------

    if cache_path.exists():
        source_mtime = os.path.getmtime(
            media_path
        )

        cache_mtime = cache_path.stat().st_mtime

        if cache_mtime >= source_mtime:
            print(
                f"[transcribe] reusing cached transcript: "
                f"{cache_path}",
                flush=True,
            )

            cached = _load_srt_cache(
                cache_path
            )

            if (
                not cached["segments"]
                or cached["duration"] <= 0.0
            ):
                print(
                    f"[transcribe] cache is empty/invalid, "
                    f"deleting: {cache_path}",
                    flush=True,
                )

                cache_path.unlink(
                    missing_ok=True
                )

            else:
                print(
                    f"[transcribe] "
                    f"{len(cached['segments'])} cached segments, "
                    f"{cached['duration']:.0f}s of audio",
                    flush=True,
                )

                return cached

    # -------------------------------------------------------
    # PROVIDER
    # -------------------------------------------------------

    provider = (
        TRANSCRIPTION_PROVIDER
        or "local"
    ).strip().lower()

    print(
        f"[transcribe] provider={provider}",
        flush=True,
    )

    if provider == "gemini":
        transcript = _transcribe_gemini(
            media_path,
            language,
        )

    elif provider == "local":
        transcript = _transcribe_whisper(
            media_path,
            language,
        )

    else:
        raise RuntimeError(
            "Unknown TRANSCRIPTION_PROVIDER: "
            f"{provider!r}. "
            "Use 'local' or 'gemini'."
        )

    # -------------------------------------------------------
    # CACHE
    # -------------------------------------------------------

    cache_path = _write_srt_cache(
        media_path,
        transcript,
    )

    print(
        f"[transcribe] wrote cache: "
        f"{cache_path}",
        flush=True,
    )

    return transcript