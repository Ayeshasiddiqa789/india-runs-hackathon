#!/usr/bin/env python3
"""Train a LightGBM regressor to predict the heuristic score and produce `submission_model.csv`.

This uses the features engineered in the baseline script and predicts the rounded out_score.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from score_candidates import load_candidates, compute_scores
import lightgbm as lgb
import csv


DATA_PATH = Path(r"c:\Hackathon\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl")
OUT = Path(r"c:\Hackathon\submission_model.csv")


def build_dataframe(scored):
    records = []
    for s in scored:
        records.append({
            "candidate_id": s["candidate_id"],
            "completeness": s.get("completeness", 0.0),
            "years": s.get("years", 0.0),
            "skill_count": s.get("skill_count", 0),
            "avg_skill_prof": s.get("avg_skill_prof", 0.0),
            "recruiter_response": s.get("recruiter_response", 0.0),
            "github": s.get("github", 0.0),
            "profile_views": s.get("profile_views", 0.0),
            "connections": s.get("connections", 0.0),
            "target": s.get("out_score", 0.0),
        })
    return pd.DataFrame.from_records(records)


def train_and_predict(df):
    features = ["completeness", "years", "skill_count", "avg_skill_prof", "recruiter_response", "github", "profile_views", "connections"]
    X = df[features].fillna(0.0).astype(float)
    y = df["target"].astype(float)
    params = {
        "objective": "regression",
        "metric": "l1",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_data_in_leaf": 20,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.9,
        "bagging_freq": 1,
        "force_col_wise": True,
        "n_jobs": -1,
        "verbosity": -1,
        "seed": 42,
    }

    # Train on a representative sample for speed; this is a ranking proxy, not a final ML benchmark.
    sample_size = min(25000, len(X))
    sample_idx = np.random.RandomState(42).choice(len(X), size=sample_size, replace=False)
    X_train = X.iloc[sample_idx]
    y_train = y.iloc[sample_idx]

    train_data = lgb.Dataset(X_train, label=y_train)
    model = lgb.train(
        params,
        train_data,
        num_boost_round=200,
        callbacks=[lgb.log_evaluation(period=0)],
    )

    preds = model.predict(X)

    df["pred"] = preds
    return df


def make_submission(df, out_path):
    # sort by predicted score desc, tie-break candidate_id
    df["score"] = df["pred"].round(4)
    df_sorted = df.sort_values(by=["score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for i, row in df_sorted.head(100).iterrows():
            rank = i + 1
            score = float(row["score"])
            reasoning = f"Auto-ranked: completeness={row['completeness']:.1f}; years={row['years']:.1f}; skills={int(row['skill_count'])}."
            writer.writerow([row["candidate_id"], rank, f"{score:.4f}", reasoning])


def main():
    candidates = list(load_candidates(DATA_PATH))
    print(f"Loaded {len(candidates)} candidates")
    # compute baseline scores (used as pseudo-targets)
    scored = compute_scores(candidates)
    df = build_dataframe(scored)
    df = train_and_predict(df)
    make_submission(df, OUT)
    print(f"Wrote model submission: {OUT}")


if __name__ == "__main__":
    main()
