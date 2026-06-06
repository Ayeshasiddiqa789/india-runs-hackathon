#!/usr/bin/env python3
"""Random-search tuner for heuristic weights.

Objective: find weights that maximize a proxy metric on the produced top-100:
 avg(profile_completeness_score) * 0.6 + avg(recruiter_response_rate) * 0.4

Produces `submission_tuned.csv` and prints the best weights and metrics.
"""
from pathlib import Path
import json
import random
import csv
from statistics import mean
from score_candidates import load_candidates, compute_scores, make_submission, DATA_PATH


OUT = Path(r"c:\Hackathon\submission_tuned.csv")


def evaluate(scored):
    # scored: list with keys out_score, recruiter_response, completeness
    top = sorted(scored, key=lambda x: (-x["out_score"], x["candidate_id"]))[:100]
    avg_compl = mean([t["completeness"] for t in top])
    avg_recruit = mean([t["recruiter_response"] for t in top])
    # proxy objective (scale matching)
    return 0.6 * (avg_compl / 100.0) + 0.4 * avg_recruit


def apply_weights_and_score(candidates, weights):
    # reuse compute_scores but override weights by modifying local variables approach:
    # We'll recompute normalized features similar to compute_scores
    rows = []
    for c in candidates:
        cid = c.get("candidate_id")
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
            "candidate_id": cid,
            "completeness": float(completeness),
            "years": float(years),
            "skill_count": int(skill_count),
            "avg_skill_prof": float(avg_skill_prof),
            "recruiter_response": float(recruiter_response),
            "github": float(github),
            "profile_views": float(profile_views),
            "connections": float(connections),
            "current_title": profile.get("current_title", "")
        })

    def normalize(values):
        lo = min(values)
        hi = max(values)
        if hi == lo:
            return [0.0 for _ in values]
        return [(v - lo) / (hi - lo) for v in values]

    completeness_n = normalize([r["completeness"] for r in rows])
    years_n = normalize([r["years"] for r in rows])
    skill_count_n = normalize([r["skill_count"] for r in rows])
    avg_skill_prof_n = normalize([r["avg_skill_prof"] for r in rows])
    recruiter_n = normalize([r["recruiter_response"] for r in rows])
    github_n = normalize([r["github"] for r in rows])
    views_n = normalize([r["profile_views"] for r in rows])
    conn_n = normalize([r["connections"] for r in rows])

    scored = []
    for i, r in enumerate(rows):
        score = (
            weights["completeness"] * completeness_n[i]
            + weights["recruiter"] * recruiter_n[i]
            + weights["years"] * years_n[i]
            + weights["skill_count"] * skill_count_n[i]
            + weights["avg_skill_prof"] * avg_skill_prof_n[i]
            + weights["github"] * github_n[i]
            + weights["views"] * views_n[i]
            + weights["conn"] * conn_n[i]
        )
        scored.append({**r, "raw_score": score})

    raw_vals = [s["raw_score"] for s in scored]
    lo = min(raw_vals)
    hi = max(raw_vals)
    if hi == lo:
        for s in scored:
            s["score"] = 0.5
    else:
        for s in scored:
            s["score"] = 0.20 + 0.79 * ((s["raw_score"] - lo) / (hi - lo))
    for s in scored:
        s["out_score"] = round(s["score"], 4)
    return scored


def random_dirichlet(keys):
    # return normalized random weights for given keys
    samples = [random.random() for _ in keys]
    s = sum(samples)
    return {k: samples[i] / s for i, k in enumerate(keys)}


def main():
    candidates = list(load_candidates(DATA_PATH))
    print(f"Loaded {len(candidates)} candidates")

    keys = ["completeness", "recruiter", "years", "skill_count", "avg_skill_prof", "github", "views", "conn"]

    best = None
    best_metric = -1
    best_weights = None

    trials = 120
    for t in range(trials):
        w = random_dirichlet(keys)
        scored = apply_weights_and_score(candidates, w)
        metric = evaluate(scored)
        if metric > best_metric:
            best_metric = metric
            best = scored
            best_weights = w
        if (t+1) % 10 == 0:
            print(f"Trial {t+1}/{trials} best_metric={best_metric:.6f}")

    print("Best metric:", best_metric)
    print("Best weights:")
    for k, v in best_weights.items():
        print(f"  {k}: {v:.4f}")

    # write final submission
    make_submission(best, OUT)
    print("Wrote tuned submission:", OUT)


if __name__ == "__main__":
    main()
