#!/usr/bin/env python3
"""Derive heuristic weights from correlations with signals (recruiter_response and completeness).

Produces `submission_auto.csv` at workspace root.
"""
from pathlib import Path
from statistics import mean
import math
import numpy as np
from score_candidates import load_candidates, make_submission


OUT = Path(r"c:\Hackathon\submission_auto.csv")


def normalize(values):
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def main():
    candidates = list(load_candidates(Path(r"c:\Hackathon\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl")))
    rows = []
    for c in candidates:
        profile = c.get("profile", {})
        completeness = c.get("redrob_signals", {}).get("profile_completeness_score", 0) or 0
        years = profile.get("years_of_experience") or 0
        skills = c.get("skills", []) or []
        skill_count = len(skills)
        prof_map = {"beginner": 0.25, "intermediate": 0.5, "advanced": 0.75, "expert": 1.0}
        avg_skill_prof = mean([prof_map.get(s.get("proficiency",""), 0) for s in skills]) if skills else 0
        recruiter_response = c.get("redrob_signals", {}).get("recruiter_response_rate", 0) or 0
        github = c.get("redrob_signals", {}).get("github_activity_score", 0) or 0
        if github < 0:
            github = 0
        profile_views = c.get("redrob_signals", {}).get("profile_views_received_30d", 0) or 0
        connections = c.get("redrob_signals", {}).get("connection_count", 0) or 0
        rows.append({
            "candidate_id": c.get("candidate_id"),
            "completeness": float(completeness),
            "years": float(years),
            "skill_count": int(skill_count),
            "avg_skill_prof": float(avg_skill_prof),
            "recruiter_response": float(recruiter_response),
            "github": float(github),
            "profile_views": float(profile_views),
            "connections": float(connections),
        })

    features = ["completeness", "years", "skill_count", "avg_skill_prof", "github", "profile_views", "connections"]
    X = {f: [r[f] for r in rows] for f in features}
    y1 = [r["recruiter_response"] for r in rows]
    y2 = [r["completeness"] for r in rows]

    # normalize features
    Xn = {f: normalize(X[f]) for f in features}

    # compute correlations with recruiter_response and completeness
    corrs = {}
    for f in features:
        a = np.array(Xn[f])
        b = np.array(y1)
        if np.std(a) == 0 or np.std(b) == 0:
            corr1 = 0.0
        else:
            corr1 = float(np.corrcoef(a, b)[0, 1])
        b2 = np.array(y2)
        if np.std(b2) == 0:
            corr2 = 0.0
        else:
            corr2 = float(np.corrcoef(a, b2)[0, 1])
        # combine correlations (weighted towards recruiter_response)
        corrs[f] = max(0.0, 0.6 * corr1 + 0.4 * corr2)

    # normalize to weights
    total = sum(corrs.values())
    if total == 0:
        weights = {k: 1.0 / len(features) for k in features}
    else:
        weights = {k: v / total for k, v in corrs.items()}

    # map to the expected keys in scoring script
    wmap = {
        "completeness": weights.get("completeness", 0),
        "recruiter": weights.get("completeness", 0),
        "years": weights.get("years", 0),
        "skill_count": weights.get("skill_count", 0),
        "avg_skill_prof": weights.get("avg_skill_prof", 0),
        "github": weights.get("github", 0),
        "views": weights.get("profile_views", 0),
        "conn": weights.get("connections", 0),
    }

    print("Derived weights:")
    for k, v in wmap.items():
        print(f"  {k}: {v:.4f}")

    # apply the weights by reusing compute pipeline from score_candidates: we'll implement a quick scorer here
    # Build scored list similar to compute_scores
    # reuse logic from tune_weights apply_weights_and_score
    from tune_weights import apply_weights_and_score
    scored = apply_weights_and_score(candidates, wmap)
    # write submission
    make_submission(scored, OUT)
    print("Wrote auto-weight submission:", OUT)


if __name__ == "__main__":
    main()
