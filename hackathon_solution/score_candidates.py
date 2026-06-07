#!/usr/bin/env python3
"""Baseline scorer: reads `candidates.jsonl`, computes heuristic scores, writes `submission.csv`.

Adjust weights as needed to improve leaderboard performance.
"""
from pathlib import Path
import json
import csv
import math
from statistics import mean


DATA_PATH = Path(r"c:\Hackathon\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl")
OUT_CSV = Path("submission.csv")
TOP_K = 100


def safe_get(d, *keys, default=None):
    v = d
    for k in keys:
        if not isinstance(v, dict):
            return default
        v = v.get(k, default)
    return v


PROF_MAP = {"beginner": 0.25, "intermediate": 0.5, "advanced": 0.75, "expert": 1.0}


def load_candidates(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def normalize(values):
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def compute_scores(candidates):
    rows = []
    for c in candidates:
        cid = c.get("candidate_id")
        profile = c.get("profile", {})

        completeness = safe_get(c, "redrob_signals", "profile_completeness_score", default=0) or 0
        years = profile.get("years_of_experience") or 0
        skills = c.get("skills", []) or []
        skill_count = len(skills)
        avg_skill_prof = mean([PROF_MAP.get(s.get("proficiency",""), 0) for s in skills]) if skills else 0
        recruiter_response = safe_get(c, "redrob_signals", "recruiter_response_rate", default=0) or 0
        github = safe_get(c, "redrob_signals", "github_activity_score", default=0) or 0
        if github < 0:
            github = 0
        profile_views = safe_get(c, "redrob_signals", "profile_views_received_30d", default=0) or 0
        connections = safe_get(c, "redrob_signals", "connection_count", default=0) or 0

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

    # normalize selected features
    completeness_n = normalize([r["completeness"] for r in rows])
    years_n = normalize([r["years"] for r in rows])
    skill_count_n = normalize([r["skill_count"] for r in rows])
    avg_skill_prof_n = normalize([r["avg_skill_prof"] for r in rows])
    recruiter_n = normalize([r["recruiter_response"] for r in rows])
    github_n = normalize([r["github"] for r in rows])
    views_n = normalize([r["profile_views"] for r in rows])
    conn_n = normalize([r["connections"] for r in rows])

    # weights — tweak these to improve leaderboard ranking
    w = {
        "completeness": 0.30,
        "recruiter": 0.22,
        "years": 0.14,
        "skill_count": 0.12,
        "avg_skill_prof": 0.10,
        "github": 0.04,
        "views": 0.04,
        "conn": 0.04,
    }

    scored = []
    for i, r in enumerate(rows):
        score = (
            w["completeness"] * completeness_n[i]
            + w["recruiter"] * recruiter_n[i]
            + w["years"] * years_n[i]
            + w["skill_count"] * skill_count_n[i]
            + w["avg_skill_prof"] * avg_skill_prof_n[i]
            + w["github"] * github_n[i]
            + w["views"] * views_n[i]
            + w["conn"] * conn_n[i]
        )
        scored.append({**r, "raw_score": score})

    # rescale raw_score to 0.20-0.99 for nicer values
    raw_vals = [s["raw_score"] for s in scored]
    lo = min(raw_vals)
    hi = max(raw_vals)
    if hi == lo:
        for s in scored:
            s["score"] = 0.5
    else:
        for s in scored:
            s["score"] = 0.20 + 0.79 * ((s["raw_score"] - lo) / (hi - lo))

    # prepare rounded output score used for ranking tie-breaks
    for s in scored:
        s["out_score"] = round(s["score"], 4)

    return scored


def make_submission(scored, out_path, top_k=TOP_K):
    # sort by rounded output score desc, tie-break candidate_id ascending
    scored_sorted = sorted(scored, key=lambda x: (-x["out_score"], x["candidate_id"]))
    if len(scored_sorted) < top_k:
        raise SystemExit(f"Not enough candidates ({len(scored_sorted)}) to produce top {top_k}")

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, s in enumerate(scored_sorted[:top_k], start=1):
            reasoning = (
                f"{s['current_title']} with {s['years']:.1f} yrs; {s['skill_count']} skills; "
                f"response rate {s['recruiter_response']:.2f}."
            )
            writer.writerow([s["candidate_id"], rank, f"{s['out_score']:.4f}", reasoning])


def main():
    if not DATA_PATH.exists():
        print(f"Data file not found: {DATA_PATH}")
        return

    candidates = list(load_candidates(DATA_PATH))
    print(f"Loaded {len(candidates)} candidates")
    scored = compute_scores(candidates)
    make_submission(scored, OUT_CSV)
    print(f"Wrote submission file: {OUT_CSV}")


if __name__ == "__main__":
    main()
