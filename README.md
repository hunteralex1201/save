# 📥 Personal Downloader — self-hosted (Docker + Caddy + iOS Shortcut)

Nijer **VPS + domain** e chole, tomar nijossho video/photo/audio downloader.
YouTube, Instagram, TikTok, Facebook, X (Twitter) + 1000+ site.

- **Server (VPS)** — `yt-dlp` diye download kore, **Caddy** auto HTTPS dey.
- **iOS Shortcut (iPhone)** — link pathay, file ferot niye Photos/Files e save kore.
- Password protected, prithibir jekono jayga theke (mobile data soho) kaj kore.

> Sudhu **personal use**. Jeisob content download er odhikar tomar ache sudhu seigulo.

---

## ⚙️ Dui ta mode — tomar VPS er obostha onujayi

| Mode | Kokhon | Compose file |
|------|--------|--------------|
| **A. Standalone** | VPS e onno kono website nei (port 80/443 fka) | `docker-compose.yml` (nijer Caddy + auto SSL) |
| **B. Existing proxy** | VPS e age theke website chole (jemon `hunterflow.cloud`) | `docker-compose.proxy.yml` + purono proxy te vhost |

> ⚠️ **Tomar khetre Mode B** — karon `hunterflow.cloud` e age theke web chole, ar seta port 80/443 dokhol kore rekheche. Standalone Caddy chalale conflict hobe. Niche **Mode B** dekho.

---

## 🅑 Mode B: VPS e age theke site ache (RECOMMENDED tomar jonno)

App ke localhost:8080 e chalai, purono reverse proxy `save.hunterflow.cloud` ke oikhane forward kore.

**1. DNS:** `save` → VPS IP (A record).

**2. Code + .env:**
```bash
git clone https://github.com/hunteralex1201/save.git downloader
cd downloader
cp .env.example .env
nano .env          # DOMAIN=save.hunterflow.cloud, DL_KEY=..., (EMAIL lagbe na)
```

**3. App চালু (port 80/443 dhore na):**
```bash
docker compose -f docker-compose.proxy.yml up -d --build
curl http://127.0.0.1:8080/health     # {"status":"ok"...} dekhle ok
```

**4. Purono proxy te `save.hunterflow.cloud` jog koro:**
- **nginx hole:** [`proxy-examples/nginx-save.conf`](proxy-examples/nginx-save.conf) `/etc/nginx/sites-available/save` e rakho →
  ```bash
  ln -s /etc/nginx/sites-available/save /etc/nginx/sites-enabled/
  nginx -t && systemctl reload nginx
  certbot --nginx -d save.hunterflow.cloud      # free SSL
  ```
- **Caddy hole:** [`proxy-examples/Caddyfile-snippet`](proxy-examples/Caddyfile-snippet) er block main Caddyfile e jog koro → `caddy reload` (SSL auto).

**5. Test:** `https://save.hunterflow.cloud/health` ✅

> Ami VPS e dhuke dekhe nebo kon proxy chole, tarpor thik config ta boshiye debo.

---

## 🅐 Mode A: VPS e onno kichu nei (standalone — Docker + Caddy)

### Ja ja lagbe
- Ubuntu/Debian VPS (root/sudo)
- Ekta domain, ar tar ekta **subdomain** (jemon `save.hunterflow.cloud`)
- DNS e ekta **A record**: `dl` → tomar VPS er IP

### ধাপ ধাপ

**1. DNS set koro** (tomar domain provider er panel e):
```
Type: A    Name: dl    Value: <VPS_IP>
```
`save.hunterflow.cloud` jeno VPS er IP te point kore. (10-30 min lagte pare.)

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
DOMAIN=save.hunterflow.cloud
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
https://save.hunterflow.cloud/health
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

## 🎚️ Quality (100% best)

- **Default** → sob theke valo **H.264 / mp4 (1080p porjonto YouTube e, IG/TikTok/FB e native full)** + AAC audio. **iPhone er Photos e nishchit chole.**
- `&best=1` → **EKEBARE max** (4K, VP9/AV1 hote pare). Photos e nao chalte pare, kintu **Files** e save hobe — archive er jonno.
- `&audio=1` → sudhu **mp3 320kbps**.

---

## 📱 iPhone Shortcut

### Soja way — ready file import koro
2 ta ready shortcut deya ache (tomar domain + key boshano):
- **Download.shortcut** — video (best iPhone quality)
- **Download-MP3.shortcut** — sudhu gaan/mp3

iPhone e file ti pathao (AirDrop / iCloud / email) → tap → **Add Shortcut**.
> Import na hole: Settings → Shortcuts → **Allow Untrusted Shortcuts** ON koro, tarpor abar tap.

Notun kore banate (domain/key change hole):
```bash
python gen_shortcut.py save.hunterflow.cloud TOMAR_DL_KEY
python gen_shortcut.py save.hunterflow.cloud TOMAR_DL_KEY --audio
```

### Ba haate banao (guaranteed, 2 min)
Shortcuts app → **+** → ei 2 ta action:

**1) Get Contents of URL**
- URL: `https://save.hunterflow.cloud/dl`
- Method: **POST**
- Request Body: **Form**, ei 2 ta field add koro:
  | Key | Value |
  |-----|-------|
  | `url` | **Shortcut Input** (magic variable) |
  | `key` | `TOMAR_DL_KEY` |
  > mp3 chaile arekta field: `audio` = `1`. Max quality chaile: `best` = `1`.
  >
  > POST form use korar karon: link e `&`, `?` thakleo encoding niye somossa hoy na.

**2) Save File**
- File: **Contents of URL** (ager action er output)
- "Ask Where to Save" **ON** → Photos/Files jekhane khushi.

Shortcut settings e **"Show in Share Sheet"** ON, accepted input e **URLs**. Nam: "Download".

**Use:** jekono app e video → **Share** → **Download** → save! 🎉

---

## 🔑 Endpoint reference

| Endpoint | Ki kore |
|----------|---------|
| `GET /health` | server + ffmpeg status |
| `GET /dl?url=<link>&key=<secret>` | video (best H.264/mp4, iPhone-friendly) |
| `GET /dl?...&best=1` | ekebare max quality (4K, Files e) |
| `GET /dl?...&audio=1` | sudhu mp3 320kbps |
| `POST /dl` (form: url, key, audio, best) | same — Shortcut er jonno (encoding-safe) |
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

- **SSL ashche na** → DNS A record thik to? `save.hunterflow.cloud` VPS IP te point korche kina `nslookup` diye dekho. Port 80/443 khola thakte hobe. `docker compose logs caddy` dekho.
- **401 Unauthorized** → Shortcut er `&key=` ar `.env` er `DL_KEY` ek to?
- **Could not download** → `docker compose build --no-cache app && docker compose up -d` (yt-dlp update).
- **Boro video timeout** → Caddy te already 30 min timeout deya. Shortcut er internet speed dekho.
