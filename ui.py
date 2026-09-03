"""UI rendering helpers for the Streamlit video editor.

Keeping rendering code here (separate from app.py and video_editor.py) makes
it easy to adapt the layout without touching the MoviePy editing logic.
"""

from typing import Optional

import streamlit as st


def render_original_preview(video_bytes: bytes, duration: Optional[float]) -> None:
    """Render the uploaded (original) video with its duration, if known."""
    st.subheader("Original video")
    st.video(video_bytes)
    if duration is not None:
        st.caption(f"Duration: {duration:.1f} seconds")


def render_result(output_path: str, extract_audio_only: bool) -> None:
    """Render the processed output (video or audio) with a download button."""
    st.subheader("Result")
    with open(output_path, "rb") as f:
        result_bytes = f.read()

    if extract_audio_only:
        st.audio(result_bytes)
        file_name = "edited_audio.mp3"
        mime = "audio/mpeg"
    else:
        st.video(result_bytes)
        file_name = "edited_video.mp4"
        mime = "video/mp4"

    st.download_button(
        "Download result",
        data=result_bytes,
        file_name=file_name,
        mime=mime,
    )
