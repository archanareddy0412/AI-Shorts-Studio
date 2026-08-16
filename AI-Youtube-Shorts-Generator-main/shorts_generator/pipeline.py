"""Local AI Shorts generation pipeline.

Supports:
1. YouTube URLs -> downloaded locally with yt-dlp
2. Local video files -> processed directly

Pipeline:
download -> transcribe -> find highlights -> adjust duration -> create clips
"""

from typing import Dict, List, Optional


# =========================================================
# DEFAULT CLIP SETTINGS
# =========================================================

# Change this number to control the duration of every clip.
#
# Examples:
#   10.0 = 10 seconds
#   15.0 = 15 seconds
#   20.0 = 20 seconds
#   30.0 = 30 seconds
#
DEFAULT_CLIP_DURATION = 20.0


def _get_video_duration(source_path: str) -> float:
    """Get the total duration of the source video using ffprobe."""

    import subprocess

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        source_path,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def _adjust_highlight_duration(
    highlight: Dict,
    clip_duration: float,
    video_duration: float,
) -> Dict:
    """
    Convert an AI-selected highlight into a fixed-duration clip.

    The highlight's start time is preserved whenever possible.

    Example:

        AI:
            81.7 -> 117.0

        clip_duration:
            20 seconds

        result:
            81.7 -> 101.7

    If the requested duration would go past the end of the video,
    the clip is moved backward so it still has the requested duration.
    """

    if clip_duration <= 0:
        raise ValueError(
            f"clip_duration must be greater than 0. Got: {clip_duration}"
        )

    original_start = float(highlight["start_time"])
    original_end = float(highlight["end_time"])

    # -----------------------------------------------------
    # Make sure the AI timestamps are inside the video.
    # -----------------------------------------------------

    original_start = max(
        0.0,
        min(original_start, video_duration),
    )

    original_end = max(
        0.0,
        min(original_end, video_duration),
    )

    # -----------------------------------------------------
    # If requested duration is longer than the entire video,
    # use the entire video.
    # -----------------------------------------------------

    if clip_duration >= video_duration:
        start = 0.0
        end = video_duration

    else:
        # -------------------------------------------------
        # Normally preserve the AI highlight's start.
        # -------------------------------------------------

        start = original_start
        end = start + clip_duration

        # -------------------------------------------------
        # If that goes beyond the end of the video,
        # move the clip backward.
        # -------------------------------------------------

        if end > video_duration:
            end = video_duration
            start = end - clip_duration

        # Safety checks
        start = max(0.0, start)
        end = min(video_duration, end)

    adjusted = dict(highlight)

    adjusted["start_time"] = round(start, 3)
    adjusted["end_time"] = round(end, 3)

    return adjusted


def _run_local(
    youtube_url: str,
    num_clips: int,
    aspect_ratio: str,
    download_format: str,
    language: Optional[str],
    clip_duration: float,
) -> Dict:

    # Local processing modules
    from .local.downloader import download_youtube_local
    from .local.transcriber import transcribe_local
    from .local.llm import call_local_llm
    from .local.clipper import crop_highlights_local
    from .highlights import get_highlights

    # ---------------------------------------------------------
    # 1. DOWNLOAD / LOCATE SOURCE VIDEO
    # ---------------------------------------------------------

    print("\n===== STEP 1: DOWNLOAD =====", flush=True)

    source_path = download_youtube_local(
        youtube_url,
        fmt=download_format,
    )

    print(
        f"[pipeline/local] source: {source_path}",
        flush=True,
    )

    # ---------------------------------------------------------
    # 2. GET VIDEO DURATION
    # ---------------------------------------------------------

    print(
        "\n===== SOURCE VIDEO INFORMATION =====",
        flush=True,
    )

    video_duration = _get_video_duration(source_path)

    print(
        f"[pipeline/local] source duration: "
        f"{video_duration:.1f}s",
        flush=True,
    )

    print(
        f"[pipeline/local] requested clip duration: "
        f"{clip_duration:.1f}s",
        flush=True,
    )

    # ---------------------------------------------------------
    # 3. TRANSCRIBE
    # ---------------------------------------------------------

    print("\n===== STEP 2: TRANSCRIBE =====", flush=True)

    transcript = transcribe_local(
        source_path,
        language=language,
    )

    if not transcript.get("segments"):
        raise RuntimeError(
            "Whisper produced no segments. "
            "The video may have no detectable speech."
        )

    # ---------------------------------------------------------
    # 4. FIND HIGHLIGHTS
    # ---------------------------------------------------------

    print("\n===== STEP 3: FIND HIGHLIGHTS =====", flush=True)

    highlights_result = get_highlights(
        transcript,
        num_clips=num_clips,
        llm_fn=call_local_llm,
    )

    all_highlights: List[Dict] = (
        highlights_result.get("highlights", [])
    )

    if not all_highlights:
        raise RuntimeError(
            "Highlight generator returned zero clips."
        )

    # ---------------------------------------------------------
    # Sort by score and keep requested number
    # ---------------------------------------------------------

    top = sorted(
        all_highlights,
        key=lambda h: int(h.get("score", 0)),
        reverse=True,
    )[:num_clips]

    print(
        f"[pipeline/local] selected "
        f"{len(top)} of {len(all_highlights)} candidates",
        flush=True,
    )

    # ---------------------------------------------------------
    # 5. ADJUST CLIP DURATIONS
    # ---------------------------------------------------------

    print(
        "\n===== STEP 4: ADJUST CLIP DURATIONS =====",
        flush=True,
    )

    adjusted_highlights: List[Dict] = []

    for i, highlight in enumerate(top, 1):

        adjusted = _adjust_highlight_duration(
            highlight=highlight,
            clip_duration=clip_duration,
            video_duration=video_duration,
        )

        print(
            f"[pipeline/local] clip {i}: "
            f"{float(highlight['start_time']):.1f}s -> "
            f"{float(highlight['end_time']):.1f}s "
            f"becomes "
            f"{adjusted['start_time']:.1f}s -> "
            f"{adjusted['end_time']:.1f}s "
            f"({adjusted['end_time'] - adjusted['start_time']:.1f}s)",
            flush=True,
        )

        adjusted_highlights.append(adjusted)

    # ---------------------------------------------------------
    # 6. CREATE SHORTS
    # ---------------------------------------------------------

    print(
        "\n===== STEP 5: CREATE SHORTS =====",
        flush=True,
    )

    shorts = crop_highlights_local(
        source_path,
        adjusted_highlights,
        aspect_ratio=aspect_ratio,
    )

    # ---------------------------------------------------------
    # 7. RETURN RESULT
    # ---------------------------------------------------------

    return {
        "mode": "local",
        "source_video_url": source_path,
        "transcript": transcript,
        "highlights": all_highlights,
        "shorts": shorts,
    }


def generate_shorts(
    youtube_url: str,
    num_clips: int = 3,
    aspect_ratio: str = "original",
    download_format: str = "720",
    language: Optional[str] = None,
    mode: str = "local",
    clip_duration: float = DEFAULT_CLIP_DURATION,
) -> Dict:
    """Run the local AI Shorts pipeline."""

    mode = (mode or "local").lower()

    if mode != "local":
        raise ValueError(
            "This version is configured for local mode only."
        )

    return _run_local(
        youtube_url=youtube_url,
        num_clips=num_clips,
        aspect_ratio=aspect_ratio,
        download_format=download_format,
        language=language,
        clip_duration=clip_duration,
    )