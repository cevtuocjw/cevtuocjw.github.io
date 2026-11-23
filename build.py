#!/usr/bin/env python3
"""Generate CEVTUOGRND — index, project pages, stats page.

Run:  python3 build.py
Data: data/projects.json + data/contributions.json
"""
from __future__ import annotations
import json, html, datetime as dt
from pathlib import Path

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
CONTRIB = json.loads((ROOT / "data/contributions.json").read_text(encoding="utf-8"))
PROJECTS = sorted(DATA["projects"], key=lambda p: p["date"], reverse=True)
SITE = DATA["site"]

RELEASE_DOWNLOADS = 98  # GitHub release assets, checked 2026-11-23
REPOS = [
    ("cevtuo-causa", "TypeScript", 0, "v0.5.1", "2026-11-19"),
    ("CEVTUO-Z", "TypeScript", 1, "v2026.10.08", "2026-11-12"),
    ("CEVTUO-RWP", "Python", 1, "v1.8", "2026-10-26"),
    ("blendergate", "Python", 0, "v1.1.0", "2026-11-02"),
    ("CEVTUO-C4EMEM", "—", 0, "v0.2.4", "2026-10-16"),
    ("syncmusic", "HTML", 0, "—", "2026-11-09"),
    ("reportpft", "CSS", 0, "—", "2026-11-12"),
    ("music-sync · private", "Python", 0, "—", "2026-11-09"),
    ("alterego · private", "TypeScript", 0, "—", "2026-11-20"),
    ("cevtuo-health · private", "Kotlin", 0, "—", "2026-09-28"),
]

STATUS_LABEL = {
    "released": "已发布",
    "beta": "内测",
    "internal": "内部",
}

def e(s: str) -> str:
    return html.escape(s, quote=True)

def esc_attr(s: str) -> str:
    return html.escape(s, quote=True)

def topbar(active: str = "") -> str:
    def cur(key: str) -> str:
        return ' aria-current="page"' if active == key else ""
    return f"""<header class="topbar">
  <div class="topbar__in">
    <nav class="topbar__side topbar__side--left" aria-label="Primary">
      <a href="/index.html"{cur("index")}>INDEX</a>
      <a href="/stats.html"{cur("stats")}>STATS</a>
    </nav>
    <a class="wordmark" href="/index.html" aria-label="CEVTUOGRND home">CEVTUOGRND</a>
    <nav class="topbar__side topbar__side--right" aria-label="Elsewhere">
      <a class="mobile-stats" href="/stats.html">STATS</a>
      <a href="https://github.com/cevtuocjw" target="_blank" rel="noopener">GITHUB ↗</a>
    </nav>
  </div>
</header>"""

def footer() -> str:
    return """<footer class="footer">
  <div>© 2026 CEVTUOGRND</div>
  <div class="fine">apps.cevtuogrnd.com · 所有软件由 CEVTUO 独立构建</div>
  <div><a href="/index.html">APPS</a> &nbsp;·&nbsp; <a href="/stats.html">STATS</a> &nbsp;·&nbsp; <a href="/privacy.html">PRIVACY</a></div>
</footer>"""

def card(p: dict, i: int, small: bool = False) -> str:
    flag = ""
    if p["status"] != "released":
        flag = f'<span class="card__flag">{e(p["statusLabel"])}</span>'
    date = p["date"]
    meta = f"{date} · {e(p['platform'])}"
    return f"""<a class="card reveal" data-status="{p['status']}" href="p/{p['slug']}.html" style="animation-delay:{min(i*55, 550)}ms">
  <div class="card__media">{flag}<img src="/{e(p['logo'])}" alt="{e(p['name'])} 标识" decoding="async"></div>
  <div class="card__body">
    <div class="card__name">{e(p['name'])}</div>
    <div class="card__cn">{e(p['cn'])}</div>
    <div class="card__meta">{meta}</div>
    <div class="card__status">{e(STATUS_LABEL[p['status']])}</div>
  </div>
</a>"""

def index_page() -> str:
    cards = "\n".join(card(p, i) for i, p in enumerate(PROJECTS))
    count = len(PROJECTS)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>CEVTUOGRND — Apps &amp; Tools</title>
<meta name="description" content="{e(SITE['intro'])}"/>
<link rel="icon" href="/assets/favicon.png"/>
<meta property="og:title" content="CEVTUOGRND — Apps &amp; Tools"/>
<meta property="og:description" content="{e(SITE['intro'])}"/>
<meta property="og:type" content="website"/>
<link rel="stylesheet" href="/assets/css/site.css"/>
</head>
<body>
{topbar("index")}
<main>
  <section class="hero">
    <p class="kicker">{e(SITE['tagline'])} · {e(SITE['year'])}</p>
    <h1>{e(SITE['wordmark'])}</h1>
    <p>{e(SITE['intro'])}</p>
  </section>
  <div class="rule"></div>
  <div class="section-head">
    <h2>PROJECTS</h2>
    <span>{count} ITEMS · SORTED BY DATE</span>
  </div>
  <div class="grid">
{cards}
  </div>
</main>
{footer()}
</body>
</html>
"""

def project_page(p: dict, next_p: dict | None) -> str:
    gallery_items = [g for g in p["gallery"]]
    stages = "".join(
        f'<button class="thumb" type="button" data-src="/{esc_attr(g)}" aria-current="{"true" if i==0 else "false"}" aria-label="查看第 {i+1} 张截图"><img src="/{esc_attr(g)}" alt="" loading="lazy"></button>'
        for i, g in enumerate(gallery_items)
    )
    if len(gallery_items) <= 1:
        thumbs = ""
    else:
        thumbs = f'<div class="thumbs" role="group" aria-label="截图">{stages}</div>'
    feat = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in p["features"])
    body = "".join(f"<p>{e(x)}</p>" for x in p["body"])

    links = p["links"]
    actions = []
    if links.get("download"):
        target = ' target="_blank" rel="noopener"' if links["download"].startswith("http") else ""
        actions.append(f'<a class="btn" href="{esc_attr(links["download"])}"{target}>{e(links["downloadLabel"])}</a>')
    else:
        actions.append(f'<span class="btn btn--off">{e(links["downloadLabel"])}</span>')
    if links.get("github"):
        actions.append(f'<a class="ghost" href="{esc_attr(links["github"])}" target="_blank" rel="noopener">GITHUB 源码 ↗</a>')
    if links.get("page") and links.get("page") != links.get("download"):
        actions.append(f'<a class="ghost" href="{esc_attr(links["page"])}">项目介绍页 →</a>')
    actions_html = "\n      ".join(actions)

    note = f'<p class="note">{e(p["note"])}</p>' if p.get("note") else ""
    gallery_html = ""
    if len(gallery_items) > 1:
        figs = "".join(
            f'<figure><img src="/{esc_attr(g)}" alt="{e(p["name"])} 截图 {i+1}" loading="lazy"><figcaption>{e(p["name"])} · {i+1:02d}</figcaption></figure>'
            for i, g in enumerate(gallery_items)
        )
        gallery_html = f"""<section class="gallery">
  <h2>SCREENS</h2>
  <div class="gallery-grid">{figs}</div>
</section>"""

    next_html = ""
    if next_p:
        next_html = f"""<section class="next">
  <a href="/p/{next_p['slug']}.html">
    <span>NEXT PROJECT</span>
    <b>{e(next_p['name'])}</b>
    <i>{e(next_p['cn'])} →</i>
  </a>
</section>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{e(p['name'])} — CEVTUOGRND</title>
<meta name="description" content="{e(p['tagline'])}"/>
<link rel="icon" href="/assets/favicon.png"/>
<meta property="og:title" content="{e(p['name'])} — CEVTUOGRND"/>
<meta property="og:description" content="{e(p['tagline'])}"/>
<meta property="og:image" content="/{esc_attr(p['cover'])}"/>
<link rel="stylesheet" href="/assets/css/site.css"/>
</head>
<body>
{topbar("")}
<main class="detail">
  <div class="crumbs"><a href="/index.html">INDEX</a><span>/</span><span>{e(p['slug'])}</span></div>
  <div class="detail__grid">
    <div class="media">
      <div class="stage"><img id="stage" src="/{esc_attr(p['cover'])}" alt="{e(p['name'])} 界面截图"></div>
      {thumbs}
    </div>
    <aside class="info">
      <img class="p-logo" src="/{esc_attr(p['logo'])}" alt="{e(p['name'])} 标识">
      <p class="p-cat">{e(p['category'])} · {p['date']}</p>
      <h1 class="p-title">{e(p['name'])}</h1>
      <p class="p-cn">{e(p['cn'])}</p>
      <p class="p-tagline">{e(p['tagline'])}</p>
      <div class="p-body">{body}</div>
      <ul class="p-features">{feat}</ul>
      <table class="p-meta">
        <tr><th>平台</th><td>{e(p['platform'])}</td></tr>
        <tr><th>版本</th><td>{e(p['version'])}</td></tr>
        <tr><th>更新</th><td>{p['date']}</td></tr>
        <tr><th>状态</th><td>{e(p['statusLabel'])}</td></tr>
      </table>
      <div class="p-actions">
      {actions_html}
      </div>
      {note}
    </aside>
  </div>
  {gallery_html}
  {next_html}
</main>
{footer()}
<script src="/assets/js/project.js" defer></script>
</body>
</html>
"""

def level(day: dict) -> int:
    c = day["contributionCount"]
    if c == 0:
        return 0
    if c <= 2:
        return 1
    if c <= 5:
        return 2
    if c <= 9:
        return 3
    return 4

def heatmap() -> str:
    weeks = CONTRIB["weeks"]
    # month labels: each span covers the weeks belonging to that month
    segs = []
    cur_month = None
    cur_label = ""
    start = 0
    for i, w in enumerate(weeks):
        d = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        key = (d.year, d.month)
        if cur_month is None:
            cur_month, cur_label, start = key, d.strftime("%b").upper(), i
        elif key != cur_month:
            segs.append((cur_label, i - start))
            cur_month, cur_label, start = key, d.strftime("%b").upper(), i
    segs.append((cur_label, len(weeks) - start))
    label_cells = [f'<span style="grid-column:span {n}">{mon}</span>' for mon, n in segs if n > 0]
    cells = []
    for w in weeks:
        for day in w["contributionDays"]:
            lv = level(day)
            attr = f' data-l{lv}' if lv else ""
            tip = f'{day["date"]} · {day["contributionCount"]} 次贡献'
            cells.append(f'<span class="heat__cell"{attr} data-tip="{tip}" title="{tip}"></span>')
    return f"""<div class="heat" role="img" aria-label="GitHub 贡献热力图，过去一年共 {CONTRIB['totalContributions']} 次贡献">
  <div class="heat__months">{''.join(label_cells)}</div>
  <div class="heat__grid">{''.join(cells)}</div>
  <div class="legend">LESS <i></i><i data-l1></i><i data-l2></i><i data-l3></i><i data-l4></i> MORE</div>
</div>"""

def metrics() -> dict:
    days = [dt.date.fromisoformat(d["date"]) for w in CONTRIB["weeks"] for d in w["contributionDays"]]
    counts = [d["contributionCount"] for w in CONTRIB["weeks"] for d in w["contributionDays"]]
    active = sum(1 for c in counts if c > 0)
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    # current streak: walk backwards from last day
    streak = 0
    for c in reversed(counts):
        if c > 0:
            streak += 1
        else:
            break
    # monthly totals last 12 months
    months = {}
    for day in (d for w in CONTRIB["weeks"] for d in w["contributionDays"]):
        key = day["date"][:7]
        months[key] = months.get(key, 0) + day["contributionCount"]
    keys = sorted(months)[-12:]
    best = max(range(len(counts)), key=lambda i: counts[i])
    return {
        "total": CONTRIB["totalContributions"],
        "active": active,
        "longest": longest,
        "streak": streak,
        "best_day": (days[best].isoformat(), counts[best]),
        "months": [(k, months[k]) for k in keys],
    }

def stats_page() -> str:
    m = metrics()
    maxm = max(v for _, v in m["months"]) or 1
    bars = "".join(
        f'<div class="bar" title="{k} · {v} 次"><i style="height:{max(2, round(v/maxm*150))}px"></i><span>{k[5:]}月</span><b>{v}</b></div>'
        for k, v in m["months"]
    )
    rows = "".join(
        f'<tr><td>{e(name)}</td><td>{e(lang)}</td><td>{stars}</td><td>{e(rel)}</td><td>{e(upd)}</td>'
        f'<td><span class="pill{" pill--live" if rel != "—" else ""}">{"released" if rel != "—" else "source"}</span></td></tr>'
        for name, lang, stars, rel, upd in REPOS
    )
    released = sum(1 for p in PROJECTS if p["status"] == "released")
    beta = sum(1 for p in PROJECTS if p["status"] == "beta")
    internal = sum(1 for p in PROJECTS if p["status"] == "internal")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>STATS — CEVTUOGRND</title>
<meta name="description" content="GitHub 贡献热力图与项目看板。"/>
<link rel="icon" href="/assets/favicon.png"/>
<link rel="stylesheet" href="/assets/css/site.css"/>
</head>
<body>
{topbar("stats")}
<main class="stats">
  <h1>DASHBOARD</h1>
  <p class="lede">GitHub 贡献热力图与项目看板。数据截至 2026-11-23，统计口径为 cevtuocjw 账号。</p>

  <div class="metric-grid">
    <div class="metric"><b>{m['total']:,}</b><span>CONTRIBUTIONS · 过去一年</span></div>
    <div class="metric"><b>{m['active']}</b><span>ACTIVE DAYS</span></div>
    <div class="metric"><b>{m['longest']}</b><span>LONGEST STREAK · DAYS</span></div>
    <div class="metric"><b>{m['streak']}</b><span>CURRENT STREAK · DAYS</span></div>
  </div>

  <section class="panel">
    <div class="panel-head"><h2>CONTRIBUTION GRAPH</h2><span>2025-11-23 → 2026-11-23 · 最高单日 {m['best_day'][1]} 次（{m['best_day'][0]}）</span></div>
    {heatmap()}
  </section>

  <section class="panel">
    <div class="panel-head"><h2>BY MONTH</h2><span>LAST 12 MONTHS</span></div>
    <div class="bars">{bars}</div>
  </section>

  <section class="panel">
    <div class="panel-head"><h2>REPOSITORIES</h2><span>{len(REPOS)} PROJECT REPOS</span></div>
    <div class="table-wrap">
      <table class="repo-table">
        <thead><tr><th>REPOSITORY</th><th>STACK</th><th>STARS</th><th>RELEASE</th><th>UPDATED</th><th>STATUS</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </section>

  <section class="panel">
    <div class="panel-head"><h2>PROJECT STATUS</h2><span>{len(PROJECTS)} PROJECTS · {RELEASE_DOWNLOADS} RELEASE DOWNLOADS</span></div>
    <div class="metric-grid">
      <div class="metric"><b>{released}</b><span>RELEASED</span></div>
      <div class="metric"><b>{beta}</b><span>BETA / 内测</span></div>
      <div class="metric"><b>{internal}</b><span>INTERNAL / 内部</span></div>
      <div class="metric"><b>{RELEASE_DOWNLOADS}</b><span>RELEASE DOWNLOADS</span></div>
    </div>
  </section>

  <section class="panel">
    <div class="panel-head"><h2>NOT ON GITHUB / NOT DISTRIBUTED</h2><span>LOCAL INVENTORY</span></div>
    <div class="status-list">
      <div class="status-item"><i class="dot"></i><div><b>CEVTUO-PGN</b><span>Chrome 扩展，只在本站分发 zip，没有公开仓库。</span></div></div>
      <div class="status-item"><i class="dot"></i><div><b>CEVNOAUATOMO</b><span>Tuna 脚本 + 使用页，没有公开仓库。</span></div></div>
      <div class="status-item"><i class="dot"></i><div><b>CEVTUO XD</b><span>APK 与手表固件，只在 /xd/ 分发，没有公开仓库。</span></div></div>
      <div class="status-item"><i class="dot dot--open"></i><div><b>师度 Alterego</b><span>私有仓库，内测中，尚未分发。</span></div></div>
      <div class="status-item"><i class="dot dot--open"></i><div><b>海外情报平台</b><span>内部 Electron 工具，未公开发行。</span></div></div>
      <div class="status-item"><i class="dot dot--open"></i><div><b>CEVTUO Health</b><span>私有仓库，Android 端 Health Connect 上报工具，未分发。</span></div></div>
      <div class="status-item"><i class="dot dot--open"></i><div><b>本地技能库</b><span>43 个 Cherry Studio 技能；其中 corner-menu / kinetic-web / apple-liquid-glass / negative-control / adaptive-contrast 等自建前端技能值得择日发布。</span></div></div>
    </div>
  </section>
</main>
{footer()}
</body>
</html>
"""

def main() -> None:
    (ROOT / "p").mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    for i, p in enumerate(PROJECTS):
        nxt = PROJECTS[(i + 1) % len(PROJECTS)]
        (ROOT / "p" / f"{p['slug']}.html").write_text(project_page(p, nxt), encoding="utf-8")
    (ROOT / "stats.html").write_text(stats_page(), encoding="utf-8")
    (ROOT / "CNAME").write_text("apps.cevtuogrnd.com\n", encoding="utf-8")
    (ROOT / ".nojekyll").touch()
    print(f"built {len(PROJECTS)} projects + index + stats")

if __name__ == "__main__":
    main()
