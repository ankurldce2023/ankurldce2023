#!/usr/bin/env python3
"""Generate the animated attack-surface radar banners for the GitHub profile README.

GitHub renders README images as <img>, so no JavaScript runs — the animation is pure CSS
inside the SVG. Run:  python3 scripts/make_radar.py   →  assets/radar-dark.svg, assets/radar-light.svg
"""
import math
from pathlib import Path

# angle: degrees clockwise from 3 o'clock · r: distance from centre
NODES = [
    (25, 70, "www", "known", "crt.name", "www.example.com"),
    (62, 135, "staging", "forgotten", "crt.name", "staging.example.com nginx/1.18.0"),
    (105, 168, ":22 ssh", "exposed", "shodan", "22/tcp OpenSSH 7.4 open"),
    (145, 78, "api", "known", "subfinder", "api.example.com"),
    (172, 165, "first.last@", "people", "harvester", "40 emails, first.last@ format"),
    (205, 132, "old-admin", "forgotten", "crt.name", "old-admin.example.com 200 OK"),
    (248, 172, "/.git", "exposed", "httpx", "/.git/HEAD 200 OK"),
    (292, 120, "/api/v1", "forgotten", "wayback", "/api/v1/users?id= still live"),
    (330, 165, "AKIA...", "exposed", "github", "AWS key in a 2023 commit"),
]

THEMES = {
    "dark": dict(bg="#0d1117", panel="#010409", line="#1f3a2a", ring="#1c3326", text="#c9d6cc", dim="#6b7d70",
                 head="#e8f3ea", known="#39ff88", forgotten="#ffb347", exposed="#ff5f6d", people="#4fc3f7", sweep="#39ff88"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", line="#d0d7de", ring="#c9e6d3", text="#24292f", dim="#6e7781",
                  head="#1f2328", known="#1a7f37", forgotten="#bc4c00", exposed="#cf222e", people="#0969da", sweep="#1a7f37"),
}

W, H = 860, 400
CX, CY, R = 200, 200, 180
PERIOD = 6.5          # seconds per sweep revolution
CYCLE = PERIOD * 2    # reveal during the first revolution, hold during the second
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def pct(angle: float) -> float:
    return angle / 360 * 50  # first revolution = first half of the cycle


def build(theme: str) -> str:
    c = THEMES[theme]
    css, nodes, links, logs = [], [], [], []
    for i, (ang, r, label, kind, src, log) in enumerate(NODES):
        x = CX + r * math.cos(math.radians(ang))
        y = CY + r * math.sin(math.radians(ang))
        right = x >= CX
        lx = x + (10 if right else -10)
        p = pct(ang)
        css.append(
            f"@keyframes n{i}{{0%,{p:.2f}%{{opacity:0}}{p + 0.6:.2f}%,96%{{opacity:1}}100%{{opacity:0}}}}"
            f".n{i}{{animation:n{i} {CYCLE}s linear infinite}}"
            f"@keyframes p{i}{{0%,{p:.2f}%{{opacity:0;transform:scale(1)}}{p + 0.3:.2f}%{{opacity:.9;transform:scale(1)}}"
            f"{p + 6:.2f}%,100%{{opacity:0;transform:scale(4.5)}}}}"
            f".p{i}{{animation:p{i} {CYCLE}s linear infinite;transform-box:fill-box;transform-origin:center}}"
        )
        col = c[kind]
        links.append(f'<line class="n{i}" x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="{col}" stroke-opacity=".35" stroke-dasharray="2 4"/>')
        nodes.append(
            f'<g class="n{i}"><circle class="p{i}" cx="{x:.1f}" cy="{y:.1f}" r="6" fill="none" stroke="{col}" stroke-width="1.5"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{col}"/>'
            f'<text x="{lx:.1f}" y="{y + 4:.1f}" text-anchor="{"start" if right else "end"}" fill="{c["text"]}" font-size="11">{label}</text></g>'
        )
        ly = 92 + i * 22
        logs.append(
            f'<g class="n{i}"><text x="470" y="{ly}" font-size="12.5"><tspan fill="{c["dim"]}">+ [{src}]</tspan>'
            f'<tspan fill="{col}" dx="8">{log}</tspan></text></g>'
        )

    n_forgot = sum(1 for n in NODES if n[3] == "forgotten")
    n_exp = sum(1 for n in NODES if n[3] == "exposed")
    css.append(
        f"@keyframes sum{{0%,50%{{opacity:0}}51%,96%{{opacity:1}}100%{{opacity:0}}}}.sum{{animation:sum {CYCLE}s linear infinite}}"
        f"@keyframes spin{{to{{transform:rotate(360deg)}}}}"
        f".sweep{{transform-origin:{CX}px {CY}px;animation:spin {PERIOD}s linear infinite}}"
        "@keyframes blink{50%{opacity:0}}.cur{animation:blink 1s steps(1) infinite}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.sweep{transform:rotate(300deg)}}"
    )
    a = math.radians(-50)
    wedge = f"M{CX},{CY} L{CX + 190},{CY} A190,190 0 0,0 {CX + 190 * math.cos(a):.1f},{CY + 190 * math.sin(a):.1f} Z"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 0 {W + 60} {H}" width="{W + 60}" height="{H}" role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">Attack surface radar</title>
<desc id="d">An animated radar discovers public assets of example.com: subdomains, an exposed .git folder, a leaked key, employee emails. 9 doors, {n_forgot} forgotten, {n_exp} exposed, 0 packets sent to the app.</desc>
<style>{"".join(css)}</style>
<defs>
<radialGradient id="bg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{c['sweep']}" stop-opacity=".10"/><stop offset="1" stop-color="{c['sweep']}" stop-opacity="0"/></radialGradient>
<linearGradient id="sw" x1="1" y1=".5" x2=".35" y2="0"><stop offset="0" stop-color="{c['sweep']}" stop-opacity=".45"/><stop offset="1" stop-color="{c['sweep']}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="-60" y="0" width="{W + 60}" height="{H}" rx="12" fill="{c['bg']}"/>
<circle cx="{CX}" cy="{CY}" r="190" fill="url(#bg)"/>
<g fill="none" stroke="{c['ring']}">
<circle cx="{CX}" cy="{CY}" r="60"/><circle cx="{CX}" cy="{CY}" r="120" stroke-dasharray="3 5"/><circle cx="{CX}" cy="{CY}" r="{R}" stroke-dasharray="1 6"/>
<line x1="10" y1="{CY}" x2="390" y2="{CY}"/><line x1="{CX}" y1="10" x2="{CX}" y2="390"/>
</g>
<g fill="{c['dim']}" font-size="9" letter-spacing=".8">
<text x="{CX + 4}" y="{CY - 62}">KNOWN</text><text x="{CX + 4}" y="{CY - 122}">FORGOTTEN</text><text x="{CX + 4}" y="{CY - 182}">UNKNOWN</text>
</g>
{"".join(links)}
<g class="sweep"><path d="{wedge}" fill="url(#sw)"/><line x1="{CX}" y1="{CY}" x2="{CX + 190}" y2="{CY}" stroke="{c['sweep']}" stroke-width="1.5"/></g>
{"".join(nodes)}
<circle cx="{CX}" cy="{CY}" r="7" fill="{c['known']}"/>
<text x="{CX}" y="{CY + 22}" text-anchor="middle" font-size="12" font-weight="700" fill="{c['head']}">example.com</text>

<rect x="450" y="30" width="390" height="340" rx="8" fill="{c['panel']}" stroke="{c['line']}"/>
<circle cx="470" cy="50" r="5" fill="{c['exposed']}"/><circle cx="487" cy="50" r="5" fill="{c['forgotten']}"/><circle cx="504" cy="50" r="5" fill="{c['known']}"/>
<text x="524" y="54" font-size="11" fill="{c['dim']}">recon — passive</text>
<text x="470" y="74" font-size="12.5" fill="{c['dim']}">$ <tspan fill="{c['head']}">recon.sh example.com</tspan><tspan class="cur" fill="{c['known']}">_</tspan></text>
{"".join(logs)}
<g class="sum"><line x1="470" y1="{92 + len(NODES) * 22 - 8}" x2="820" y2="{92 + len(NODES) * 22 - 8}" stroke="{c['line']}" stroke-dasharray="3 3"/>
<text x="470" y="{92 + len(NODES) * 22 + 12}" font-size="12.5" fill="{c['head']}"><tspan fill="{c['known']}">$</tspan> {len(NODES)} doors · <tspan fill="{c['forgotten']}">{n_forgot} forgotten</tspan> · <tspan fill="{c['exposed']}">{n_exp} exposed</tspan></text>
<text x="470" y="{92 + len(NODES) * 22 + 32}" font-size="12.5" fill="{c['dim']}">0 packets sent to the app.</text></g>
</svg>
"""


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    for t in THEMES:
        (out / f"radar-{t}.svg").write_text(build(t), encoding="utf-8")
        print(f"wrote assets/radar-{t}.svg")
