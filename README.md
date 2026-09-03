# MPYVids

MPYVids is a Streamlit app for editing videos using
[MoviePy](https://zulko.github.io/moviepy/index.html), a Python video editing
library. Upload a video, trim it, resize it, change its playback speed,
adjust its volume, or extract its audio track, then download the result.

## Does this need an API key?

No. MoviePy is a local Python library (built on top of ffmpeg) that runs
entirely on the server hosting the app - it is not a web API, so there is no
API key or account for the end user to provide. This is a deliberate change
from the previous version of this repository, which was a generic template
for wrapping a third-party HTTP API and asked users to paste an API key into
the UI.

## Can this run on Streamlit Community Cloud's free tier?

Yes, with a few caveats to keep in mind:

- **ffmpeg dependency**: MoviePy needs an ffmpeg binary. `requirements.txt`
  includes `imageio-ffmpeg`, which downloads a self-contained ffmpeg binary
  at install time, so no extra setup is required. `packages.txt` also
  requests the `ffmpeg` apt package as a fallback, since Streamlit Community
  Cloud reads that file to install system packages.
- **Resource limits**: Community Cloud free-tier apps are capped at roughly
  1 GB of RAM and share CPU with other apps on the host. Video encoding is
  CPU/RAM intensive, so keep uploaded videos short and/or low-resolution.
  Very large files may time out or exceed the memory limit.
- **Ephemeral storage**: Uploaded videos and processed output are written to
  temporary files on disk and are not persisted - they are removed after each
  run and do not survive an app restart or reboot. This is fine for a
  single edit-and-download workflow but means the app is not a video store.
- **No GPU**: All encoding happens on CPU, so processing is slower than a
  GPU-accelerated pipeline, which is another reason to keep clips short.

In short: yes, this is possible, and no API key is required, but the app is
best suited to short clips rather than long/high-resolution video due to the
free tier's CPU, memory, and time constraints.

## Contents

- `app.py` — Streamlit entrypoint: file upload, edit options, and calls into
  `video_editor.process_video()`
- `video_editor.py` — MoviePy editing logic (trim, resize, speed, volume,
  audio extraction), independent of Streamlit so it stays easy to test
- `ui.py` — rendering helpers for previewing the original/edited video and
  offering a download button
- `requirements.txt` — Python dependencies (`streamlit`, `moviepy`,
  `imageio-ffmpeg`)
- `packages.txt` — system packages for Streamlit Community Cloud (`ffmpeg`)

## Quick start

1. Install dependencies

   ```
   pip install -r requirements.txt
   ```

2. Run locally

   ```
   streamlit run app.py
   ```

3. Upload a video, choose your edits (trim range, resize scale, speed,
   volume, or audio-only extraction), click **Process video**, and download
   the result.

## Deploying to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a new app on [share.streamlit.io](https://share.streamlit.io),
   pointing at `app.py` as the entrypoint.
3. Community Cloud automatically installs `requirements.txt` (Python
   packages) and `packages.txt` (apt packages, including `ffmpeg`) before
   starting the app - no other configuration is required.

## Extending the app

- Add more MoviePy effects (crop, rotate, fade in/out, text overlays, etc.)
  in `video_editor.py`.
- Add tests for `video_editor.process_video()` using short generated sample
  clips.
- Add a file-size/duration limit in `app.py` if you plan to host this for
  public use, to stay within the free tier's resource limits.
