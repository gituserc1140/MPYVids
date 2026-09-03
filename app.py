"""MPYVids: a Streamlit video editor built on MoviePy.

MoviePy (https://zulko.github.io/moviepy/index.html) is a local Python video
editing library, not a web API, so this app never needs an API key. Upload a
video, choose one or more edits (trim, resize, change speed, adjust volume, or
extract audio), then download the result.

Run locally:
  pip install -r requirements.txt
  streamlit run app.py
"""

import os
import tempfile

import streamlit as st

import ui
from video_editor import EditOptions, SUPPORTED_EXTENSIONS, get_duration, process_video

st.set_page_config(page_title="MPYVids - Video Editor", layout="centered")

st.header("MPYVids")
st.write(
    "Edit videos in your browser using [MoviePy](https://zulko.github.io/moviepy/index.html). "
    "No API key required - all processing happens locally on the server."
)

uploaded_file = st.file_uploader("Upload a video", type=list(SUPPORTED_EXTENSIONS))

if uploaded_file is not None:
    video_bytes = uploaded_file.getvalue()
    suffix = "." + uploaded_file.name.rsplit(".", 1)[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as input_tmp:
        input_tmp.write(video_bytes)
        input_path = input_tmp.name

    try:
        duration = get_duration(input_path)
    except Exception as exc:  # pragma: no cover - defensive, surfaced to user
        st.error(f"Could not read the uploaded video: {exc}")
        os.remove(input_path)
        st.stop()

    ui.render_original_preview(video_bytes, duration)

    st.subheader("Edit options")
    col1, col2 = st.columns(2)
    with col1:
        start = st.number_input("Start (seconds)", min_value=0.0, max_value=float(duration), value=0.0, step=1.0)
    with col2:
        end = st.number_input("End (seconds)", min_value=0.0, max_value=float(duration), value=float(duration), step=1.0)

    scale = st.slider("Resize (scale factor)", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
    speed = st.slider("Speed (playback multiplier)", min_value=0.25, max_value=4.0, value=1.0, step=0.25)
    volume = st.slider("Volume (multiplier)", min_value=0.0, max_value=3.0, value=1.0, step=0.1)
    extract_audio_only = st.checkbox("Extract audio only (produces an audio file instead of a video)")

    if st.button("Process video"):
        if end <= start:
            st.error("End time must be greater than start time.")
        else:
            options = EditOptions(
                start=start,
                end=end,
                scale=scale,
                speed=speed,
                volume=volume,
                extract_audio_only=extract_audio_only,
            )
            output_suffix = ".mp3" if extract_audio_only else ".mp4"
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=output_suffix).name

            with st.spinner("Processing video..."):
                try:
                    process_video(input_path, output_path, options)
                    ui.render_result(output_path, extract_audio_only)
                except Exception as exc:
                    st.error(f"Failed to process video: {exc}")
                finally:
                    if os.path.exists(output_path):
                        os.remove(output_path)

    # Clean up the temporary input file. Streamlit reruns the script on every
    # interaction, so this file is recreated (and removed) on each run.
    os.remove(input_path)
else:
    st.info("Upload a video to get started (supported formats: " + ", ".join(SUPPORTED_EXTENSIONS) + ").")
