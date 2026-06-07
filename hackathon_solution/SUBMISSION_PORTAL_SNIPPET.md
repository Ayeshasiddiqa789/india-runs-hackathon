Paste this exact text into the portal description / comments field (edit bracketed fields):

Project: Intelligent Candidate Discovery & Ranking
Team: [Your Team Name]
Team Leader: [Your Full Name]

Short description:
Heuristic + LightGBM ensemble to rank candidates. The pipeline computes an interpretable weighted heuristic, trains a LightGBM regressor on those heuristic scores as pseudo‑targets, and ensembles both scores to produce a stable top‑100 ranking. The submission includes the validated CSV and reproducible code.

Artifacts uploaded:
- `submission_final.pdf` — ranked output (100 rows), validated for the challenge.
- `submission_final.csv` — original CSV (included in repo and package).
- `submission_final_package.zip` — packaged artifacts (CSV, scripts, demo).
- `India_Runs_Presentation_from_template.pptx` — presentation slides (also available as PDF in repo root).

Repo: https://github.com/Ayeshasiddiqa789/india-runs-hackathon

Repro (short): create virtualenv → `pip install -r hackathon_solution/requirements.txt` → `python score_candidates.py && python train_model.py && python ensemble_and_package.py` → `submission_final.csv` will be generated and packaged.

Contact: [Your email or GitHub handle]
