"""Local clipping using FFmpeg only.

Cuts highlights from the original video without:
- cropping
- resizing
- face tracking
- OpenCV

The output keeps the original video's resolution and aspect ratio.
"""

import os
import subprocess
from typing import Dict, List, Optional

from ..config import LOCAL_OUTPUT_DIR


def crop_clip_local(
    source_path: str,
    start_time: float,
    end_time: float,
    aspect_ratio: str,
    out_path: str,
) -> str:
    """
    Cut one highlight from the source video.

    IMPORTANT:
    aspect_ratio is intentionally ignored.

    The output keeps the original video's:
    - resolution
    - aspect ratio
    - audio
    """

    duration = float(end_time) - float(start_time)

    if duration <= 0:
        raise ValueError(
            f"Invalid clip duration: {start_time} -> {end_time}"
        )

    print(
        f"[clip/local] cutting {start_time:.1f}s -> "
        f"{end_time:.1f}s ({duration:.1f}s)",
        flush=True,
    )

    cmd = [
        "ffmpeg",
        "-y",

        # Input
        "-ss",
        f"{float(start_time):.3f}",
        "-i",
        source_path,

        # Duration of this clip
        "-t",
        f"{duration:.3f}",

        # Keep original video dimensions/aspect ratio.
        # Re-encode for reliable cutting.
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",

        # Keep audio
        "-c:a",
        "aac",
        "-b:a",
        "192k",

        # Avoid unnecessary metadata
        "-map_metadata",
        "-1",

        out_path,
    ]

    subprocess.run(cmd, check=True)

    if not os.path.exists(out_path):
        raise RuntimeError(
            f"FFmpeg completed but output was not created: {out_path}"
        )

    print(
        f"[clip/local] created: {out_path}",
        flush=True,
    )

    return out_path


def crop_highlights_local(
    source_path: str,
    highlights: List[Dict],
    aspect_ratio: str = "original",
    out_dir: Optional[str] = None,
) -> List[Dict]:
    """
    Create one clip for every selected highlight.

    No cropping or resizing is performed.
    """

    out_dir = out_dir or LOCAL_OUTPUT_DIR

    os.makedirs(out_dir, exist_ok=True)

    results: List[Dict] = []

    total = len(highlights)

    print(
        f"[clip/local] creating {total} clips "
        f"without cropping",
        flush=True,
    )

    for i, h in enumerate(highlights, 1):

        out_path = os.path.join(
            out_dir,
            f"short_{i:02d}.mp4",
        )

        print(
            f"[clip/local] {i}/{total}: "
            f"{h.get('title', '(untitled)')}",
            flush=True,
        )

        try:

            crop_clip_local(
                source_path=source_path,
                start_time=float(h["start_time"]),
                end_time=float(h["end_time"]),
                aspect_ratio="original",
                out_path=out_path,
            )

            results.append(
                {
                    **h,
                    "clip_url": out_path,
                }
            )

        except Exception as e:

            print(
                f"[clip/local] {i} failed: {e}",
                flush=True,
            )

            results.append(
                {
                    **h,
                    "clip_url": None,
                    "error": str(e),
                }
            )

    successful = sum(
        1
        for item in results
        if item.get("clip_url")
    )

    print(
        f"[clip/local] finished: "
        f"{successful}/{total} clips created",
        flush=True,
    )

    return results