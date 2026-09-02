# Private sharing

This repository is designed to be shared privately for review. It contains synthetic demonstration data only and must remain private unless every ABL-specific reference is deliberately reassessed for public release.

## Audience boundary

The remote repository may contain:

- the working synthetic application and audience-safe proof pages;
- synthetic scenarios, prompts, controls, tests and evaluation evidence;
- architecture, brand and sharing documentation; and
- deliberately prepared follow-up artifacts under `share/`.

Keep the following local and out of the panel-facing repository or follow-up pack:

- exact presenter scripts, timings and transitions;
- likely interview questions and rehearsed answers;
- demonstration-day setup, reset and recovery notes;
- leadership or role-fit rehearsal material; and
- historical checkpoints containing stale meeting or hosting instructions.

Those local presenter materials live under `documents/demo/` and are ignored by version control. The historical `documents/general/2026-09-01-demo-checkpoint.md` is also ignored. Before pushing, confirm neither path appears in the tracked-file list.

Removing a file from the current tracked tree does not remove an earlier committed copy from repository history. If the panel will receive source-repository access, use a clean repository/export containing only the approved current tree, or deliberately rewrite the existing history after separate review and approval. If the panel receives only the generated presentation site or an approved artifact under `share/`, ignored presenter documents and repository history are not included.

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
