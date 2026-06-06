Project: Intelligent Candidate Discovery & Ranking — Final Submission

Included files
- `submission_ensemble.csv` — final ensembled submission (top 100)
- `submission_model.csv` — model-based submission (for reference)
- `submission.csv` — baseline heuristic submission
- `top20.json` — top-20 candidates for quick demo
- `ensemble_and_package.py` — script used to create the ensemble and package
- `score_candidates.py`, `train_model.py`, `tune_weights.py`, `auto_weights.py` — reproduction scripts

How I built the solution (summary for judges)
- Data parsing and validation: used the provided `candidates.jsonl` and the challenge validator (`validate_submission.py`).
- Baseline: handcrafted heuristic combining profile completeness, years of experience, skill counts and recruiter response rate. Produced `submission.csv`.
- Model: trained a LightGBM regressor (fast sampled fit) on the heuristic scores as pseudo-targets to learn nonlinear interactions. Produced `submission_model.csv`.
- Ensemble: averaged baseline and model scores to produce `submission_ensemble.csv` (this file is submitted).

Why this approach
- The heuristic gives a strong initial ranking and is robust. The LightGBM model learns interactions and improves ranking signals. Averaging stabilizes results for fairness and better proxy metrics.

How to reproduce
1. Create a Python virtualenv and install dependencies:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r c:\Hackathon\hackathon_solution\requirements.txt
```

2. Generate baseline submission:
```bat
python c:\Hackathon\hackathon_solution\score_candidates.py
```

3. Train model and generate model submission:
```bat
python c:\Hackathon\hackathon_solution\train_model.py
```

4. Create ensemble and package:
```bat
python c:\Hackathon\hackathon_solution\ensemble_and_package.py
```

Demo
- Open `c:\Hackathon\hackathon_solution\demo.html` in a browser (it reads `top20.json` and shows the top candidates).

Contact
- If you need edits or a video demo, tell me what to highlight and I will produce it.
