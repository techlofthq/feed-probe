"""One-off check: does a GitHub-hosted server get answers from three bookmaker feeds? Sends one small read-only request to each (what a browser would load)
and prints only the status, the size and whether the reply is data or a block page. It stores and sends nothing."""
import json
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
CHECKS = {
    "bet9ja": ("https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetEventsInDailyBundleV3?DISP=1001&DISPH=0&SPORTID=1&LIMIT=20",
               {"Referer": "https://sports.bet9ja.com/", "Origin": "https://sports.bet9ja.com"}),
    "betano": ("https://www.betano.ng/api/sports/upcoming/calendar/FOOT/?timeZoneId=Africa/Lagos&hours=24",
               {"Referer": "https://www.betano.ng/", "X-Requested-With": "XMLHttpRequest"}),
    "betway": ("https://feeds-roa2.betwayafrica.com/br/_apis/sport/v1/BetBook/Upcoming/?countryCode=NG&sportId=soccer&Skip=0&Take=1&cultureCode=en-US&isEsport=false&boostedOnly=false"
               "&marketTypes=%5BWin%2FDraw%2FWin%5D", {"Referer": "https://www.betway.com.ng/"}),
}


def get(url, headers):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read(400000), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(4000), dict(e.headers)
    except Exception as e:                                   # noqa: BLE001
        return 0, str(e).encode()[:200], {}


try:
    info = json.loads(get("https://ipinfo.io/json", {})[1])
    print("runner:", info.get("country"), info.get("org"))
except Exception as e:                                       # noqa: BLE001
    print("runner: unknown", e)
for name, (url, headers) in CHECKS.items():
    status, body, h = get(url, headers)
    text = body.decode("utf-8", "replace")
    try:
        json.loads(text)
        kind = "JSON data"
    except ValueError:
        kind = "JSON data (cut at 400 KB)" if text.lstrip().startswith(("{", "[")) else "block/challenge page" if ("just a moment" in text.lower() or "cloudflare" in text.lower() or "captcha" in text.lower()) else "not JSON"
    print(f"{name}: HTTP {status}, {len(body)} bytes, {kind}, server={h.get('Server', h.get('server', ''))}")
