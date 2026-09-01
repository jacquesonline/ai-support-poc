# Private sharing

This repository is designed to be shared privately for review. It contains synthetic demonstration data only and must remain private unless every ABL-specific reference is deliberately reassessed for public release.

## GitHub repository access

1. Create the repository as **Private**.
2. Push the default branch.
3. In GitHub, open **Settings → Collaborators and teams → Add people**.
4. Invite the intended reviewer using their GitHub username or email address.
5. Share the repository URL only after the invitation has been accepted.

A private GitHub repository link provides source-code access; it does not provide a running web application. The reviewer must have a GitHub account and accept the invitation.

## Running the demonstration

The safest review route is credential-free local execution:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
.\start-demo.ps1
```

Then open `http://127.0.0.1:8017/`.

## Security controls

- Never commit `.env`, API keys, access tokens, credentials or real matter data.
- Keep optional live adapters disabled for the shared review.
- Use no real client, employee, matter, application or job-search content.
- Re-run the test suite and secret scan before each shared revision.
- If browser access to a hosted application is required, use a separate authenticated hosting service and review its access controls; do not assume a private GitHub repository makes a deployed website private.
