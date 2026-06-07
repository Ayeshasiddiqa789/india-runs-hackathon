Demo script and slide outline

Slide 1: Title
- Project: Intelligent Candidate Discovery & Ranking
- Team: Solo — 2026 fresher

Slide 2: Problem & Dataset
- What we solved: rank candidates by hire-ability using platform signals.
- Data: anonymized profiles + redrob signals (completeness, recruiter response, github score, views).

Slide 3: Approach
- Baseline heuristic (explain features and weights).
- Learned model (LightGBM) trained on heuristic pseudo-targets.
- Ensemble: averaging baseline + model for stability.

Slide 4: Metrics & Validation
- Validation: submission format rules, tie-break correctness.
- Proxy ranking metrics: avg completeness and recruiter_response in top-100.

Slide 5: Demo
- Open `hackathon_solution\demo.html` to view top-20.
- Show `submission_ensemble.csv` and explain top picks.

Slide 6: Next steps / Improvements
- Train pairwise ranker with human labels or A/B test.
- Add NLP features from `summary` and `career_history` descriptions.

Script notes
- 2-minute demo: 30s problem, 40s approach, 30s demo, 20s closing.
