# 📥 Personal Downloader — self-hosted (Docker + Caddy + iOS Shortcut)

Nijer **VPS + domain** e chole, tomar nijossho video/photo/audio downloader.
YouTube, Instagram, TikTok, Facebook, X (Twitter) + 1000+ site.

- **Server (VPS)** — `yt-dlp` diye download kore, **Caddy** auto HTTPS dey.
- **iOS Shortcut (iPhone)** — link pathay, file ferot niye Photos/Files e save kore.
- Password protected, prithibir jekono jayga theke (mobile data soho) kaj kore.

> Sudhu **personal use**. Jeisob content download er odhikar tomar ache sudhu seigulo.

---

## 🚀 VPS e deploy (production — Docker + Caddy)

### Ja ja lagbe
- Ubuntu/Debian VPS (root/sudo)
- Ekta domain, ar tar ekta **subdomain** (jemon `dl.tomarsite.com`)
- DNS e ekta **A record**: `dl` → tomar VPS er IP

### ধাপ ধাপ

**1. DNS set koro** (tomar domain provider er panel e):
```
Type: A    Name: dl    Value: <VPS_IP>
```
`dl.tomarsite.com` jeno VPS er IP te point kore. (10-30 min lagte pare.)

**2. VPS e code ano:**
```bash
git clone <tomar-github-repo-url> downloader
cd downloader
```

**3. `.env` banao:**
```bash
cp .env.example .env
nano .env
```
Boshao:
```
DOMAIN=dl.tomarsite.com
EMAIL=tomar@email.com
DL_KEY=<lomba-random-secret>      # banate:  openssl rand -hex 24
```

**4. Deploy (ek command):**
```bash
sudo bash deploy.sh
```
Eta Docker install korbe (na thakle), firewall e 80/443 khulbe, build kore চালু korbe.
Caddy nijei **free SSL** niye nebe.

**5. Test:**
```
https://dl.tomarsite.com/health
```
`{"status":"ok","ffmpeg":true,...}` dekhle ✅ ready.

### Pore kaj korar command
```bash
docker compose logs -f          # log dekho
docker compose restart          # restart
docker compose up -d --build    # code update er por
docker compose down             # bondho
```
yt-dlp update korte (site change hole): `docker compose build --no-cache app && docker compose up -d`

---

## 📱 iPhone Shortcut banano

Shortcuts app → **+** → ei 2 ta action:

**1) Get Contents of URL**
- Method: **GET**
- URL:
  ```
  https://dl.tomarsite.com/dl?url=[Shortcut Input]&key=TOMAR_DL_KEY
  ```
  > `[Shortcut Input]` = magic variable boshao (type koro na). `TOMAR_DL_KEY` = .env er DL_KEY.

**2) Save File**
- File: **Contents of URL**
- "Ask Where to Save" **ON** → Photos/Files jekhane khushi.

Shortcut settings e **"Show in Share Sheet"** ON koro, accepted input e **URLs** select koro. Nam dao "Download".

**Use:** jekono app e video → **Share** → tomar **Download** shortcut → file save! 🎉

**Sudhu mp3 (gaan)** chaile alada shortcut, URL er sheshe `&audio=1`:
```
https://dl.tomarsite.com/dl?url=[Shortcut Input]&key=TOMAR_DL_KEY&audio=1
```

---

## 🔑 Endpoint reference

| Endpoint | Ki kore |
|----------|---------|
| `GET /health` | server + ffmpeg status |
| `GET /dl?url=<link>&key=<secret>` | video download (mp4) |
| `GET /dl?url=<link>&key=<secret>&audio=1` | sudhu mp3 audio |
| `GET /info?url=<link>&key=<secret>` | download na kore title/duration |

---

## 🍪 Private / age-restricted content (optional, powerful)

Private Instagram, age-restricted YouTube, member content namate hole browser er cookies dao:

1. Browser e logged-in thaka obostha te "Get cookies.txt" extension diye `cookies.txt` export koro.
2. `cookies.txt` VPS er project folder e rakho.
3. `docker-compose.yml` e `app:` service er niche un-comment koro:
   ```yaml
   environment:
     - COOKIES_FILE=/app/cookies.txt
   volumes:
     - ./cookies.txt:/app/cookies.txt:ro
   ```
4. `docker compose up -d`

---

## 🖥️ VPS chara — sudhu nijer PC te (alternative)

Windows PC te local test korte: `winget install Gyan.FFmpeg` koro, tarpor `start.bat`
double-click. Eki WiFi te iPhone theke `http://<PC-IP>:8000/dl?url=...` use korbe.
(Bistarito comment server.py / start.bat e.)

---

## 🛠️ Somossa hole

- **SSL ashche na** → DNS A record thik to? `dl.tomarsite.com` VPS IP te point korche kina `nslookup` diye dekho. Port 80/443 khola thakte hobe. `docker compose logs caddy` dekho.
- **401 Unauthorized** → Shortcut er `&key=` ar `.env` er `DL_KEY` ek to?
- **Could not download** → `docker compose build --no-cache app && docker compose up -d` (yt-dlp update).
- **Boro video timeout** → Caddy te already 30 min timeout deya. Shortcut er internet speed dekho.
