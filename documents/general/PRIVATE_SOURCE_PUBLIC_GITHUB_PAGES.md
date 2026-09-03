# Deploy a private source repository to a public GitHub Pages repository

## Purpose

Keep the complete `ai-support-poc` source repository private while publishing only its intentionally public, static presentation edition on GitHub Pages.

This pattern is appropriate because GitHub Pages is public even where a plan permits publishing from a private repository. It prevents the application source, tests, local-only material and history from becoming public, but it does **not** make the generated website private.

## Recommended repository layout

Use two repositories owned by the same GitHub account:

| Role | Repository | Visibility | Contents |
| --- | --- | --- | --- |
| Source | `jacquesonline/ai-support-poc-source` | Private | The FastAPI application, tests, documentation and export script. |
| Published site | `jacquesonline/ai-support-poc` | Public | Only the generated static GitHub Pages output. |

Using `ai-support-poc` as the public repository preserves the existing address:

`https://jacquesonline.github.io/ai-support-poc/`

The exporter currently sets its base path to `/ai-support-poc/`. If the public repository is instead called `ai-support-poc-site`, first change `BASE` in `scripts/export_pages.py` to `/ai-support-poc-site/`; the published URL and every generated internal link will then use that name.

## One-time setup

1. Create the empty **public** publishing repository. Do not add the full project or any private material to it.
2. Make the source repository private. If it is currently named `ai-support-poc`, rename it to `ai-support-poc-source` before creating the public repository with the original name.
3. In the public repository, open **Settings → Pages**. Choose **Deploy from a branch**, select `main` and `/ (root)`, then save.
4. Create a fine-grained personal access token (PAT):
   - **Name:** `PAGES_DEPLOY_TOKEN`
   - **Resource owner:** `jacquesonline`
   - **Repository access:** only `ai-support-poc` (the public publishing repository)
   - **Repository permissions:** **Contents: Read and write**

   The token does not need access to the private source repository: GitHub Actions checks that repository out with its built-in `GITHUB_TOKEN`.
5. In the **private** source repository, add the token as an Actions secret named `PAGES_DEPLOY_TOKEN` under **Settings → Secrets and variables → Actions**.

## Workflow for this project

Create `.github/workflows/deploy-public-pages.yml` in the private source repository.

```yaml
name: Publish static presentation to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: public-pages-publish
  cancel-in-progress: true

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Check out private source
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Export the public static edition
        run: python scripts/export_pages.py

      - name: Publish to public Pages repository
        env:
          PAGES_DEPLOY_TOKEN: ${{ secrets.PAGES_DEPLOY_TOKEN }}
          TARGET_REPOSITORY: jacquesonline/ai-support-poc
          SOURCE_DIRECTORY: _site
        shell: bash
        run: |
          set -euo pipefail
          test -d "$SOURCE_DIRECTORY"

          git config --global user.name "github-actions[bot]"
          git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"

          publish_directory="$(mktemp -d)"
          git clone "https://x-access-token:${PAGES_DEPLOY_TOKEN}@github.com/${TARGET_REPOSITORY}.git" "$publish_directory"

          rsync -a --delete --exclude .git "$SOURCE_DIRECTORY/" "$publish_directory/"

          cd "$publish_directory"
          touch .nojekyll
          git add --all
          if git diff --cached --quiet; then
            echo "No public-site changes to publish."
            exit 0
          fi

          git commit -m "Publish ${GITHUB_REPOSITORY}@${GITHUB_SHA}"
          git push origin main
```

The current export command is intentionally dependency-free and writes the public edition to `_site`. It excludes server-backed FastAPI behaviour; only the browser-safe presentation is published.

## Custom domain (optional)

If the public Pages site uses `jacquesonline.biz`, add this immediately after the `rsync` line in the workflow so every deployment retains the setting:

```bash
printf '%s\n' 'jacquesonline.biz' > "$publish_directory/CNAME"
```

Then configure the domain in the public repository’s **Settings → Pages** and add the GitHub-provided DNS records at the domain registrar. Enable **Enforce HTTPS** after the certificate is issued.

## Publish and verify

1. Commit the workflow to the private source repository and push to `main`, or run it from the **Actions** tab.
2. Check the workflow log; it must show the static export and a successful push to the public repository.
3. Open `https://jacquesonline.github.io/ai-support-poc/` in a signed-out/private browser session.
4. Check the home page, navigation, static assets and each public download/link.
5. In the public repository, confirm that it contains only `_site` output: HTML, CSS, JavaScript, SVG assets and `.nojekyll`—not application source, `.env` files, tests or private documentation.

## Safety checklist

- Review the generated `_site` directory before the first public deployment and after any material content change.
- Keep the source repository private and never copy its Git history into the public publishing repository.
- Use a fine-grained PAT scoped to the public target repository only; rotate or revoke it if it is exposed or no longer needed.
- `rsync --delete` makes the public repository exactly match the generated output. Keep persistent Pages settings, such as `CNAME`, in the workflow or in the export output so they are not removed on the next deployment.
- GitHub Pages is a public presentation channel. Do not export credentials, personal data, confidential employer information or local presenter material.

## Official references

- [GitHub Pages availability and limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [GitHub Pages custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages)
- [Fine-grained personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
