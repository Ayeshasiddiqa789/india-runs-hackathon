# India Runs Hackathon Presentation Outline

## Slide 1: Title
- Project: Intelligent Candidate Discovery & Ranking
- Team: Solo, 2026 fresher
- Challenge: India Runs Data & AI Challenge

## Slide 2: Problem Statement
- Rank candidates for opportunities using profile and platform signals.
- Goal: produce a top-100 ranked list that follows the submission rules.

## Slide 3: Data Used
- Candidate profile data from `candidates.jsonl`
- Key signals: profile completeness, years of experience, skills, recruiter response rate, GitHub score, views, connections

## Slide 4: Solution Approach
- Baseline heuristic ranking using feature weights
- LightGBM model trained on heuristic scores as pseudo-targets
- Final ensemble by averaging baseline + model scores

## Slide 5: Validation
- Used the provided validator rules
- Ensured exactly 100 rows, valid candidate IDs, unique ranks, and tie-break by candidate ID

## Slide 6: Results
- Final submission file: `submission_final.csv`
- Demo top-20 file: `top20.json`
- Reproducible scripts included in `hackathon_solution/`

## Slide 7: Demo
- Open `demo.html` to show top candidates
- Explain why the top profiles are ranked higher

## Slide 8: Why This Works
- Heuristic captures obvious signals
- Model learns non-linear interactions
- Ensemble improves stability and ranking quality

## Slide 9: Future Improvements
- Train a pairwise ranker with label feedback
- Add NLP features from summaries and job history
- Add more robust validation and model tuning

## Slide 10: Closing
- Final deliverable: `submission_final.csv`
- GitHub repo: `https://github.com/Ayeshasiddiqa789/india-runs-hackathon`
