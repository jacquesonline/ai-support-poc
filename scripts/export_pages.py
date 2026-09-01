"""Export presentation routes as a GitHub Pages-compatible static site."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "app" / "static"
OUTPUT = ROOT / "_site"
BASE = "/ai-support-poc/"

PAGES = {
    "overview.html": "index.html",
    "workbench-menu.html": "workbench/index.html",
    "cheatsheet.html": "cheatsheet/index.html",
    "proof-matter.html": "proofs/matter/index.html",
    "proof-support.html": "proofs/support/index.html",
    "proof-harvey.html": "proofs/harvey/index.html",
    "harvey-demo.html": "harvey-demo/index.html",
    "proof-improvement.html": "proofs/improvement/index.html",
    "proof-value.html": "proofs/value/index.html",
}


def pages_html(source: str) -> str:
    html = (STATIC / source).read_text(encoding="utf-8")
    if "/static/brand.css" not in html:
        html = html.replace("</head>", '<link rel="stylesheet" href="/static/brand.css"></head>')

    replacements = {
        'href="/static/': f'href="{BASE}static/',
        'src="/static/': f'src="{BASE}static/',
        'href="/proofs/matter"': f'href="{BASE}proofs/matter/"',
        'href="/proofs/support"': f'href="{BASE}proofs/support/"',
        'href="/proofs/harvey"': f'href="{BASE}proofs/harvey/"',
        'href="/proofs/improvement"': f'href="{BASE}proofs/improvement/"',
        'href="/proofs/value"': f'href="{BASE}proofs/value/"',
        'href="/harvey-demo"': f'href="{BASE}harvey-demo/"',
        'href="/workbench/matter"': f'href="{BASE}workbench/"',
        'href="/workbench/support"': f'href="{BASE}workbench/"',
        'href="/workbench/harvey"': f'href="{BASE}harvey-demo/"',
        'href="/workbench/improvement"': f'href="{BASE}workbench/"',
        'href="/workbench/value"': f'href="{BASE}workbench/"',
        'href="/workbench/full"': 'href="https://github.com/jacquesonline/ai-support-poc"',
        'href="/workbench#harvey"': f'href="{BASE}workbench/"',
        'href="/workbench"': f'href="{BASE}workbench/"',
        'href="/cheatsheet"': f'href="{BASE}cheatsheet/"',
        'href="/#control-room"': f'href="{BASE}workbench/"',
        'href="/#harvey"': f'href="{BASE}workbench/"',
        'href="/#improvement"': f'href="{BASE}workbench/"',
        'href="/#proof-5"': f'href="{BASE}workbench/"',
        'href="/"': f'href="{BASE}"',
        "Open matter scenarios →": "Return to the proof selector →",
        "Run a support case →": "Return to the proof selector →",
        "Open Harvey readiness evidence →": "Return to the proof selector →",
        "Open regression evidence →": "Return to the proof selector →",
        "Open value evidence →": "Return to the proof selector →",
        "The combined control room is retained for detailed technical evidence only.": "The full interactive control room requires the local FastAPI runtime.",
        "Open the full evidence workbench": "View the source and local run instructions",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    banner = (
        '<div class="pages-boundary">GitHub Pages presentation edition · '
        'interactive evidence runs in the local application</div>'
    )
    return html.replace("</body>", f"{banner}</body>")


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / "static").mkdir(parents=True)

    for asset in STATIC.iterdir():
        if asset.is_file() and asset.suffix in {".css", ".js", ".svg"}:
            shutil.copy2(asset, OUTPUT / "static" / asset.name)

    for source, destination in PAGES.items():
        target = OUTPUT / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(pages_html(source), encoding="utf-8")

    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main()
