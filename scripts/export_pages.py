"""Export presentation routes as a GitHub Pages-compatible static site."""

from pathlib import Path
import os
import shutil
import stat


ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "app" / "static"
# An override supports clean verification without replacing a locally synced
# deployment directory. GitHub Actions uses the default `_site` location.
OUTPUT = Path(os.environ.get("PAGES_OUTPUT_DIR", ROOT / "_site"))
BASE = "/ai-support-poc/"

PAGES = {
    "overview.html": "index.html",
    "pages-workbench.html": "workbench/index.html",
    "cheatsheet.html": "cheatsheet/index.html",
    "proof-matter.html": "proofs/matter/index.html",
    "proof-support.html": "proofs/support/index.html",
    "proof-harvey.html": "proofs/legal-ai/index.html",
    "harvey-demo.html": "legal-ai-demo/index.html",
    "proof-improvement.html": "proofs/improvement/index.html",
    "proof-value.html": "proofs/value/index.html",
}


def remove_readonly(func, path: str, _exc_info) -> None:
    """Allow generated OneDrive files to be replaced during a clean export."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def pages_html(source: str) -> str:
    html = (STATIC / source).read_text(encoding="utf-8")
    if "/static/brand.css" not in html:
        html = html.replace("</head>", '<link rel="stylesheet" href="/static/brand.css"></head>')

    replacements = {
        'href="/static/': f'href="{BASE}static/',
        'src="/static/': f'src="{BASE}static/',
        'href="/proofs/matter"': f'href="{BASE}proofs/matter/"',
        'href="/proofs/support"': f'href="{BASE}proofs/support/"',
        'href="/proofs/harvey"': f'href="{BASE}proofs/legal-ai/"',
        'href="/proofs/improvement"': f'href="{BASE}proofs/improvement/"',
        'href="/proofs/value"': f'href="{BASE}proofs/value/"',
        'href="/harvey-demo"': f'href="{BASE}legal-ai-demo/"',
        'href="/workbench/matter"': f'href="{BASE}workbench/#matter"',
        'href="/workbench/support"': f'href="{BASE}workbench/#access"',
        'href="/workbench/harvey"': f'href="{BASE}legal-ai-demo/"',
        'href="/workbench/improvement"': f'href="{BASE}workbench/#improvement"',
        'href="/workbench/value"': f'href="{BASE}workbench/#improvement"',
        'href="/workbench/full"': f'href="{BASE}workbench/"',
        'href="/workbench#harvey"': f'href="{BASE}legal-ai-demo/"',
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
        "Open the full evidence workbench": "Open the interactive demonstration",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    # The public edition is deliberately organisation- and vendor-neutral.
    # Keep the richer interview prototype local; never let its scenario labels
    # imply an employer relationship, a vendor integration, or private access.
    public_wording = {
        "ABL-style": "legal-services",
        "ABL’s": "the organisation’s",
        "ABL": "the organisation",
        "Harvey": "AI-assisted legal work",
        "harvey-demo.css": "legal-ai-demo.css",
        "harvey-demo.js": "legal-ai-demo.js",
        "harvey": "legalAi",
    }
    for old, new in public_wording.items():
        html = html.replace(old, new)

    # Repair compound phrases after the intentionally simple name replacement.
    html = html.replace("AI-assisted legal work-enabled legal work", "AI-assisted legal work")
    html = html.replace("AI-assisted legal work legal work", "AI-assisted legal work")
    html = html.replace("AI-assisted legal work work product", "AI-assisted legal-work product")
    html = html.replace("A AI-assisted", "An AI-assisted")
    html = html.replace("My proposed the organisation operating model", "My proposed operating model")
    html = html.replace("representative the organisation pilots", "representative pilots")
    html = html.replace("an the organisation budget", "an organisation budget")

    banner = (
        '<div class="pages-boundary">Independent synthetic demonstration · '
        'no private client, employer or vendor data</div>'
    )
    return html.replace("</body>", f"{banner}</body>")


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT, onerror=remove_readonly)
    (OUTPUT / "static").mkdir(parents=True)

    for asset in STATIC.iterdir():
        # This browser-only presentation must not carry the local FastAPI
        # workbench client, even as an unused file. It contains server-route
        # assumptions and internal prototype identifiers.
        if asset.name == "demo.js":
            continue
        if asset.is_file() and asset.suffix in {".css", ".js", ".svg"}:
            target_name = asset.name.replace("harvey-demo", "legal-ai-demo")
            target = OUTPUT / "static" / target_name
            if asset.suffix in {".css", ".js"}:
                content = asset.read_text(encoding="utf-8")
                content = content.replace("ABL", "the organisation")
                content = content.replace("Harvey", "AI-assisted legal work")
                content = content.replace("harvey-demo", "legal-ai-demo")
                content = content.replace("harvey", "legalAi")
                content = content.replace("--abl-", "--legal-")
                target.write_text(content, encoding="utf-8")
            else:
                shutil.copy2(asset, target)

    for source, destination in PAGES.items():
        target = OUTPUT / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(pages_html(source), encoding="utf-8")

    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main()
