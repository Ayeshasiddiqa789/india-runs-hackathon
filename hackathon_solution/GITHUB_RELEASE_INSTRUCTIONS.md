Two ways to attach `submission_final.pdf` to a GitHub Release.

1) Quick (web UI)
- Push your latest commits to GitHub (ensure `submission_final.pdf` is in the repo root or workspace to upload from your machine).
- Open: https://github.com/Ayeshasiddiqa789/india-runs-hackathon/releases
- Click "Draft a new release" → give a tag (e.g. `v1.0`) and title "India Runs — Submission".
- In "Attach binaries by dropping them here or selecting them", upload `submission_final.pdf` (and optionally `submission_final_package.zip`).
- Add release notes (paste contents of `SUBMISSION_PORTAL_SNIPPET.md`) and Publish release.

2) CLI (requires GitHub CLI `gh` installed and authenticated):
```
gh auth login
cd path/to/your/local/repo
git add submission_final.pdf
git commit -m "Add submission_final.pdf for release"
git push
# create release and attach asset
gh release create v1.0 submission_final.pdf --repo Ayeshasiddiqa789/india-runs-hackathon --title "India Runs — Submission" --notes "See repo for code and demo."
```

Notes:
- Release assets are downloadable by judges; publishing a release is often more convenient than embedding large files in the repo history.
- If you prefer, I can prepare a ready-to-run `gh` command with an exact release note body — tell me which tag/title you want.
