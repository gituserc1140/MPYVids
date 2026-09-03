"""Video editing helpers built on top of MoviePy (https://zulko.github.io/moviepy).

This module keeps all MoviePy-specific logic separate from the Streamlit UI so
that it stays easy to test and reuse. All functions operate on local file
paths (typically temporary files created from an uploaded video) and do not
call out to any external web API, so no API key is ever required.
"""

from dataclasses import dataclass
from typing import Optional

from moviepy import VideoFileClip

SUPPORTED_EXTENSIONS = ("mp4", "mov", "avi", "mkv", "webm")


@dataclass
class EditOptions:
    """Options describing how an input video should be edited.

    start/end are given in seconds and are optional (None keeps the original
    boundary). scale is a resize factor (1.0 = original size). speed is a
    playback speed multiplier. volume is an audio volume multiplier.
    extract_audio_only, when True, produces an audio-only file instead of a
    video file.
    """

    start: Optional[float] = None
    end: Optional[float] = None
    scale: float = 1.0
    speed: float = 1.0
    volume: float = 1.0
    extract_audio_only: bool = False


def get_duration(input_path: str) -> float:
    """Return the duration (in seconds) of the video at input_path."""
    with VideoFileClip(input_path) as clip:
        return clip.duration


def process_video(input_path: str, output_path: str, options: EditOptions) -> str:
    """Apply the requested edits to input_path and write the result to output_path.

    Returns output_path for convenience. Raises any exception encountered
    while reading, editing, or writing the clip so callers can surface a
    helpful error message to the user.
    """
    with VideoFileClip(input_path) as clip:
        edited = clip

        if options.start is not None or options.end is not None:
            start = options.start or 0
            end = options.end if options.end is not None else edited.duration
            edited = edited.subclipped(start, end)

        if options.speed and options.speed != 1.0:
            edited = edited.with_speed_scaled(options.speed)

        if options.scale and options.scale != 1.0:
            edited = edited.resized(options.scale)

        if options.volume and options.volume != 1.0 and edited.audio is not None:
            edited = edited.with_volume_scaled(options.volume)

        if options.extract_audio_only:
            if edited.audio is None:
                raise ValueError("The selected clip has no audio track to extract.")
            edited.audio.write_audiofile(output_path, logger=None)
        else:
            edited.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                logger=None,
            )

    return output_path
