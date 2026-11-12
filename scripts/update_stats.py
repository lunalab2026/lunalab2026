# -*- coding: utf-8 -*-
"""
Gera assets/telemetry.svg: painel de estatisticas reais do GitHub no tema Matrix.

Uso:
  python scripts/update_stats.py           # busca dados na API (usa GITHUB_TOKEN/STATS_TOKEN se houver)
  python scripts/update_stats.py --empty   # painel inicial "aguardando dados"
  python scripts/update_stats.py --mock    # dados ficticios, apenas para visualizar o layout

So usa a biblioteca padrao do Python.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

LOGIN = os.environ.get("GH_LOGIN") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "lunalab2026"
TOKEN = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "telemetry.svg")
GREEN = "#00ff41"


# --------------------------------------------------------------- coleta
def api(url, payload=None):
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "lunalab-telemetry"},
    )
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_rest():
    user = api(f"https://api.github.com/users/{LOGIN}")
    repos, page = [], 1
    while True:
        chunk = api(f"https://api.github.com/users/{LOGIN}/repos?per_page=100&type=owner&page={page}")
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r.get("fork")]
    langs = {}
    for r in own:
        try:
            for k, v in api(r["languages_url"]).items():
                langs[k] = langs.get(k, 0) + v
        except Exception as e:  # um repo com problema nao derruba o painel
            print("aviso: linguagens de", r.get("name"), "->", e, file=sys.stderr)
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "login": user.get("login", LOGIN),
        "created": user.get("created_at"),
        "followers": user.get("followers", 0),
        "repos": user.get("public_repos", len(repos)),
        "stars": sum(r.get("stargazers_count", 0) for r in own),
        "langs": [(k, v * 100.0 / total) for k, v in top],
    }


def fetch_contrib():
    """Contribuicoes dos ultimos 12 meses (GraphQL). Retorna None se falhar."""
    if not TOKEN:
        return None
    q = (
        "query($l:String!){user(login:$l){contributionsCollection{"
        "totalCommitContributions totalPullRequestContributions totalIssueContributions "
        "restrictedContributionsCount contributionCalendar{totalContributions "
        "weeks{contributionDays{contributionCount date}}}}}}"
    )
    try:
        res = api("https://api.github.com/graphql", json.dumps({"query": q, "variables": {"l": LOGIN}}).encode())
        c = res["data"]["user"]["contributionsCollection"]
        cal = c["contributionCalendar"]
        days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
        weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
        return {
            "commits": c["totalCommitContributions"],
            "prs": c["totalPullRequestContributions"],
            "issues": c["totalIssueContributions"],
            "total": cal["totalContributions"],
            "days": days,
            "weeks": weeks[-52:],
        }
    except Exception as e:
        print("aviso: GraphQL indisponivel ->", e, file=sys.stderr)
        return None


def streaks(days):
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    i, cur = len(days) - 1, 0
    if i >= 0 and days[i][1] == 0:  # hoje ainda sem commit nao quebra a sequencia
        i -= 1
    while i >= 0 and days[i][1] > 0:
        cur += 1
        i -= 1
    return cur, longest


# --------------------------------------------------------------- render
def num(n):
    return f"{int(n):,}".replace(",", ".")


def render(d):
    c = d.get("contrib")
    now = d.get("updated")
    age_days = None
    if d.get("created"):
        created = dt.datetime.strptime(d["created"], "%Y-%m-%dT%H:%M:%SZ")
        age_days = max(0, ((now or dt.datetime.utcnow()) - created).days)

    cur = best_run = best_day = None
    if c:
        cur, best_run = streaks(c["days"])
        best_day = max((n for _, n in c["days"]), default=0)

    kpis = [
        ("REPOSITÓRIOS", d["repos"]),
        ("ESTRELAS", d["stars"]),
        ("SEGUIDORES", d["followers"]),
        ("COMMITS 12M", c["commits"] if c else None),
        ("PULL REQUESTS", c["prs"] if c else None),
        ("ISSUES", c["issues"] if c else None),
    ]
    tiles = []
    for i, (label, val) in enumerate(kpis):
        x = 24 + i * 160.8
        shown = "--" if val is None else num(val)
        fill = "#2f6b3c" if val is None else "#c8ffd4"
        tiles.append(
            f'<g class="fi" style="animation-delay:{i*0.12:.2f}s">'
            f'<rect x="{x:.1f}" y="62" width="148" height="84" rx="6" fill="#04140a" stroke="#00b32b" stroke-opacity=".45"/>'
            f'<text x="{x+14:.1f}" y="86" font-size="11" fill="#00c832" letter-spacing="1">{escape(label)}</text>'
            f'<text x="{x+14:.1f}" y="128" font-size="34" font-weight="bold" fill="{fill}" filter="url(#glow)">{shown}</text></g>'
        )

    # linguagens
    shades = ["#00ff41", "#00d936", "#00b32b", "#008f11", "#006b0d"]
    rows = []
    langs = d["langs"]
    if langs:
        for i, (name, pct) in enumerate(langs):
            y = 206 + i * 21
            w = max(3.0, 340 * pct / 100)
            rows.append(
                f'<text x="32" y="{y+9}" font-size="12" fill="#c8ffd4">{escape(name)}</text>'
                f'<rect x="150" y="{y}" width="340" height="11" rx="5" fill="#0b2a12"/>'
                f'<rect class="gx" style="animation-delay:{0.3+i*0.15:.2f}s" x="150" y="{y}" width="{w:.1f}" height="11" rx="5" fill="{shades[i]}"/>'
                f'<text x="574" y="{y+9}" font-size="12" text-anchor="end" fill="#00ff41">{pct:.1f}%</text>'
            )
    else:
        rows.append(
            '<text class="bl" x="304" y="262" font-size="13" text-anchor="middle" fill="#00c832">'
            "[ aguardando o primeiro commit com código... ]</text>"
        )

    # sequencia
    def stat(x, y, label, value):
        v = "--" if value is None else value
        col = "#2f6b3c" if value is None else "#c8ffd4"
        return (
            f'<text x="{x}" y="{y}" font-size="11" fill="#00c832" letter-spacing="1">{label}</text>'
            f'<text x="{x}" y="{y+30}" font-size="26" font-weight="bold" fill="{col}" filter="url(#glow)">{v}</text>'
        )

    unit = lambda n: None if n is None else f"{num(n)} {'dia' if n == 1 else 'dias'}"
    right = (
        stat(628, 206, "SEQUÊNCIA ATUAL", unit(cur))
        + stat(808, 206, "MAIOR SEQUÊNCIA", unit(best_run))
        + stat(628, 262, "MELHOR DIA (CONTRIB.)", None if best_day is None else num(best_day))
        + stat(808, 262, "NA MATRIX HÁ", unit(age_days))
    )

    # atividade
    base, maxh, step = 412, 44, 944 / 52
    bars = []
    weeks = c["weeks"] if c else []
    peak = max(weeks) if weeks else 0
    has_activity = peak > 0
    for i in range(52):
        x = 28 + i * step
        n = weeks[i] if i < len(weeks) else 0
        h = max(2.0, maxh * n / peak) if has_activity else 2.0
        col = GREEN if n > 0 else "#0b2a12"
        op = 1 if n > 0 else 1
        bars.append(
            f'<rect class="up" style="animation-delay:{0.4+i*0.02:.2f}s" x="{x:.1f}" y="{base-h:.1f}" '
            f'width="{step-4.5:.1f}" height="{h:.1f}" rx="2" fill="{col}" fill-opacity="{op}"/>'
        )
    if not has_activity:
        bars.append(
            '<text class="bl" x="500" y="388" font-size="13" text-anchor="middle" fill="#00c832">'
            "[ sem atividade registrada ainda — o primeiro commit acende a Matrix ]</text>"
        )
    total_txt = "--" if not c else num(c["total"])
    sync = "sync pendente" if not now else f"sync {now:%Y-%m-%d %H:%M} UTC"

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 440" width="1000" height="440" role="img" aria-label="Telemetria GitHub de {escape(d["login"])}: {num(d["repos"])} repositórios, {num(d["stars"])} estrelas, {num(d["followers"])} seguidores">
<title>TELEMETRIA // {escape(d["login"])}</title>
<defs>
<style>
text{{font-family:'Courier New',Courier,'Liberation Mono','DejaVu Sans Mono',monospace}}
.fi{{animation:fi .8s ease-out both}}
.gx{{transform-box:fill-box;transform-origin:left center;animation:gx 1.1s ease-out both}}
.up{{transform-box:fill-box;transform-origin:center bottom;animation:gy .9s ease-out both}}
.bl{{animation:bl 1.6s steps(1) infinite}}
.sc{{animation:sc 5s linear infinite}}
@keyframes fi{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes gx{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes gy{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes bl{{0%,60%{{opacity:1}}61%,100%{{opacity:.25}}}}
@keyframes sc{{from{{transform:translateY(-60px)}}to{{transform:translateY(440px)}}}}
</style>
<filter id="glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="scg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".09"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<pattern id="ln" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".3"/></pattern>
</defs>
<rect width="1000" height="440" rx="10" fill="#020a03"/>
<text x="24" y="34" font-size="15" font-weight="bold" fill="{GREEN}" filter="url(#glow)">&gt; TELEMETRIA.SYS // {escape(d["login"])}</text>
<text x="976" y="34" font-size="12" text-anchor="end" fill="#2f8f45">{sync}</text>
<rect x="24" y="45" width="952" height="1" fill="#003b00"/>
{"".join(tiles)}
<rect x="16" y="160" width="576" height="156" rx="6" fill="#030f06" stroke="#00b32b" stroke-opacity=".3"/>
<text x="32" y="184" font-size="13" font-weight="bold" fill="{GREEN}" letter-spacing="1">LINGUAGENS</text>
{"".join(rows)}
<rect x="608" y="160" width="376" height="156" rx="6" fill="#030f06" stroke="#00b32b" stroke-opacity=".3"/>
<text x="628" y="184" font-size="13" font-weight="bold" fill="{GREEN}" letter-spacing="1">SEQUÊNCIA</text>
{right}
<rect x="16" y="330" width="968" height="96" rx="6" fill="#030f06" stroke="#00b32b" stroke-opacity=".3"/>
<text x="28" y="350" font-size="13" font-weight="bold" fill="{GREEN}" letter-spacing="1">ATIVIDADE // 52 SEMANAS</text>
<text x="972" y="350" font-size="12" text-anchor="end" fill="#2f8f45">total 12m: {total_txt}</text>
{"".join(bars)}
<rect class="sc" width="1000" height="60" fill="url(#scg)"/>
<rect width="1000" height="440" rx="10" fill="url(#ln)"/>
<rect x="1.5" y="1.5" width="997" height="437" rx="9" fill="none" stroke="{GREEN}" stroke-opacity=".5" stroke-width="1.5"/>
</svg>
'''


def mock():
    import random
    random.seed(7)
    days = []
    start = dt.date(2025, 11, 12)
    for i in range(365):
        days.append(((start + dt.timedelta(days=i)).isoformat(), random.choice([0, 0, 1, 2, 3, 5, 8, 12])))
    weeks = [sum(n for _, n in days[i:i + 7]) for i in range(0, 364, 7)]
    return {
        "login": LOGIN, "created": "2026-01-10T12:00:00Z", "followers": 42, "repos": 12, "stars": 128,
        "langs": [("TypeScript", 46.2), ("JavaScript", 24.8), ("Python", 17.5), ("CSS", 7.9), ("HTML", 3.6)],
        "contrib": {"commits": 812, "prs": 64, "issues": 21, "total": 977, "days": days, "weeks": weeks[-52:]},
        "updated": dt.datetime(2026, 11, 12, 3, 15),
    }


def main():
    flag = sys.argv[1] if len(sys.argv) > 1 else ""
    out = sys.argv[2] if len(sys.argv) > 2 else OUT
    if flag == "--mock":
        data = mock()
    elif flag == "--empty":
        data = {"login": LOGIN, "created": None, "followers": 0, "repos": 0, "stars": 0, "langs": [], "contrib": None, "updated": None}
    else:
        try:
            data = fetch_rest()
        except Exception as e:
            print("erro ao consultar a API:", e, file=sys.stderr)
            if os.path.exists(out):
                print("mantendo o painel anterior.", file=sys.stderr)
                return 0
            return 1
        data["contrib"] = fetch_contrib()
        data["updated"] = dt.datetime.utcnow().replace(second=0, microsecond=0)
    svg = render(data)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("ok ->", os.path.abspath(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
