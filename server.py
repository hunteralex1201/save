"""
Personal media downloader server (yt-dlp + FastAPI) — production build.

iOS Shortcut theke link pathale, ei server video/photo/audio download kore
file ti shortcut ke ferot dey -> shortcut Photos/Files e save kore.

Supported: YouTube, Instagram, TikTok, Facebook, X(Twitter) + 1000+ site.
"""

import os
import re
import glob
import time
import shutil
import uuid
import asyncio
import logging
import mimetypes

from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from starlette.background import BackgroundTask
import yt_dlp

# ----------------------------------------------------------------------------
# Config (environment variable diye control kora jay)
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", os.path.join(BASE_DIR, "downloads"))
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Password. Production e oboshyoi set korbe (docker .env e DL_KEY).
API_KEY = os.environ.get("DL_KEY", "").strip()

# Optional: private/age-restricted content er jonno cookies.txt path.
COOKIES_FILE = os.environ.get("COOKIES_FILE", "").strip()

# Purono download koto purono hole muche debe (second). Default 1 ghonta.
MAX_FILE_AGE = int(os.environ.get("MAX_FILE_AGE", "3600"))

# Ek shathe koyta download cholbe (server bachano).
MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", "3"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("downloader")


def _find_ffmpeg_dir():
    """ffmpeg PATH e na thakleo winget/common jaygay khuje ber kori."""
    exe = shutil.which("ffmpeg")
    if exe:
        return os.path.dirname(exe)
    candidates = []
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        candidates.append(os.path.join(local, "Microsoft", "WinGet", "Links"))
        candidates += glob.glob(os.path.join(
            local, "Microsoft", "WinGet", "Packages",
            "Gyan.FFmpeg*", "**", "bin"), recursive=True)
    for d in candidates:
        if os.path.isfile(os.path.join(d, "ffmpeg.exe")):
            return d
    return None


_FFMPEG_DIR = _find_ffmpeg_dir()
HAS_FFMPEG = _FFMPEG_DIR is not None
if _FFMPEG_DIR and _FFMPEG_DIR not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

_sem = asyncio.Semaphore(MAX_CONCURRENT)

app = FastAPI(title="Personal Downloader", docs_url=None, redoc_url=None)


def _safe(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    return name.strip() or "download"


def _check_key(key: str):
    if API_KEY and key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing key")


def _cleanup_old():
    """Purono download folder gulo muche dei (disk bhore na jay)."""
    now = time.time()
    for d in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
        try:
            if os.path.isdir(d) and now - os.path.getmtime(d) > MAX_FILE_AGE:
                shutil.rmtree(d, ignore_errors=True)
        except OSError:
            pass


def _do_download(url: str, audio: bool, best: bool = False):
    """yt-dlp diye download kore (path, out_dir) ferot dey. Blocking.

    audio=True  -> sob theke valo audio -> mp3 320kbps
    best=True   -> EKEBARE max quality (4K/VP9/AV1 hote pare; iPhone Photos e
                   nao chalte pare, Files e thakbe)
    default     -> max quality H.264/mp4 (iPhone e GUARANTEED chole) + fallback
    """
    req_id = uuid.uuid4().hex[:12]
    out_dir = os.path.join(DOWNLOAD_DIR, req_id)
    os.makedirs(out_dir, exist_ok=True)

    ydl_opts = {
        "outtmpl": os.path.join(out_dir, "%(title).100s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "concurrent_fragment_downloads": 8,
        "retries": 5,
        "fragment_retries": 10,
        "socket_timeout": 30,
        "trim_file_name": 120,
    }
    if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    if audio:
        # Sob theke valo audio -> mp3 320 (ffmpeg lage)
        ydl_opts["format"] = "bestaudio/best"
        if HAS_FFMPEG:
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }]
    elif not HAS_FFMPEG:
        # ffmpeg na thakle ek-file best (merge kora jay na)
        ydl_opts["format"] = "best"
    elif best:
        # Ekebare max — codec ja-i hok (4K AV1/VP9 o ney)
        ydl_opts["format"] = "bv*+ba/b"
        ydl_opts["merge_output_format"] = "mp4"
    else:
        # Default: max quality H.264 (avc1) + m4a -> mp4. iPhone e nishchit chole.
        # Na pawa gele HEVC, tarpor jekono best.
        ydl_opts["format"] = (
            "bv*[vcodec^=avc1]+ba[ext=m4a]/"
            "bv*[ext=mp4]+ba[ext=m4a]/"
            "b[ext=mp4]/bv*+ba/b"
        )
        ydl_opts["merge_output_format"] = "mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    files = [f for f in glob.glob(os.path.join(out_dir, "*")) if os.path.isfile(f)]
    if not files:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail="Download failed: no file produced")

    files.sort(key=os.path.getsize, reverse=True)
    return files[0], out_dir


@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html><html><head><meta charset=utf-8>
<title>Personal Downloader</title>
<style>body{font-family:system-ui;max-width:640px;margin:60px auto;padding:0 20px;color:#222}
code{background:#f3f3f3;padding:2px 6px;border-radius:4px}h1{font-size:22px}</style></head>
<body><h1>📥 Personal Downloader</h1>
<p>Server cholche. Eta ekta private API — iOS Shortcut er jonno.</p>
<p>Use: <code>/dl?url=&lt;link&gt;&amp;key=&lt;secret&gt;</code> (video) ba <code>&amp;audio=1</code> (mp3).</p>
</body></html>"""


@app.get("/health")
def health():
    return {"status": "ok", "ffmpeg": HAS_FFMPEG, "auth_required": bool(API_KEY)}


async def _handle(url: str, audio: bool, best: bool, key: str, client: str):
    """GET ar POST — dui jaygar shared logic."""
    _check_key(key)
    if not url:
        raise HTTPException(status_code=422, detail="url lage")
    _cleanup_old()
    log.info("download %s audio=%s best=%s from %s", url, audio, best, client)

    async with _sem:
        try:
            # yt-dlp blocking, tai threadpool e chalai
            path, out_dir = await asyncio.to_thread(_do_download, url, audio, best)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not download: {e}")

    filename = _safe(os.path.basename(path))
    media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    log.info("sending %s (%s bytes)", filename, os.path.getsize(path))
    # File pathanor por out_dir muche dei
    return FileResponse(
        path, media_type=media_type, filename=filename,
        background=BackgroundTask(shutil.rmtree, out_dir, True),
    )


@app.get("/dl")
async def dl_get(
    request: Request,
    url: str = Query(..., description="Video/post link"),
    audio: int = Query(0, description="1 dile sudhu mp3 audio"),
    best: int = Query(0, description="1 dile ekebare max quality (4K, Files e)"),
    key: str = Query("", description="DL_KEY set thakle dorkar"),
):
    client = request.client.host if request.client else "?"
    return await _handle(url, bool(audio), bool(best), key, client)


@app.post("/dl")
async def dl_post(
    request: Request,
    url: str = Form(...),
    audio: int = Form(0),
    best: int = Form(0),
    key: str = Form(""),
):
    # iOS Shortcut POST form pathaale link encoding niye jhamela hoy na
    client = request.client.host if request.client else "?"
    return await _handle(url, bool(audio), bool(best), key, client)


@app.get("/info")
async def info(url: str = Query(...), key: str = Query("")):
    _check_key(key)
    try:
        def _extract():
            opts = {"quiet": True, "no_warnings": True, "noplaylist": True}
            if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
                opts["cookiefile"] = COOKIES_FILE
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        data = await asyncio.to_thread(_extract)
        return JSONResponse({
            "title": data.get("title"),
            "duration": data.get("duration"),
            "uploader": data.get("uploader"),
            "thumbnail": data.get("thumbnail"),
            "extractor": data.get("extractor"),
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.on_event("startup")
def _startup():
    _cleanup_old()
    if not API_KEY:
        log.warning("DL_KEY set kora nei — server password chara cholche! Production e DL_KEY dao.")
    log.info("ffmpeg=%s  auth=%s  concurrency=%s", HAS_FFMPEG, bool(API_KEY), MAX_CONCURRENT)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
