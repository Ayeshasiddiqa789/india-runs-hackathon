#!/usr/bin/env python3
"""Hyperparameter random search for LightGBM and ensemble with baseline.

Produces `c:\Hackathon\submission_final.csv` (best ensemble) and updates package.
"""
from pathlib import Path
import random
import numpy as np
import csv
from score_candidates import load_candidates, compute_scores
from tune_weights import apply_weights_and_score
import lightgbm as lgb
import json
import zipfile


OUT = Path(r"c:\Hackathon\submission_final.csv")
BASE = Path(r"c:\Hackathon\submission.csv")
MODEL = Path(r"c:\Hackathon\submission_model.csv")
PKG = Path(r"c:\Hackathon\hackathon_solution\submission_final_package.zip")


def features_from_candidates(candidates):
    rows = []
    for c in candidates:
        cid = c.get('candidate_id')
        profile = c.get('profile', {})
        completeness = c.get('redrob_signals', {}).get('profile_completeness_score', 0) or 0
        years = profile.get('years_of_experience') or 0
        skills = c.get('skills', []) or []
        skill_count = len(skills)
        prof_map = {"beginner": 0.25, "intermediate": 0.5, "advanced": 0.75, "expert": 1.0}
        avg_skill_prof = np.mean([prof_map.get(s.get('proficiency',''),0) for s in skills]) if skills else 0
        recruiter = c.get('redrob_signals', {}).get('recruiter_response_rate', 0) or 0
        github = c.get('redrob_signals', {}).get('github_activity_score', 0) or 0
        if github < 0:
            github = 0
        views = c.get('redrob_signals', {}).get('profile_views_received_30d', 0) or 0
        conn = c.get('redrob_signals', {}).get('connection_count', 0) or 0
        rows.append({
            'candidate_id': cid,
            'completeness': float(completeness),
            'years': float(years),
            'skill_count': int(skill_count),
            'avg_skill_prof': float(avg_skill_prof),
            'recruiter': float(recruiter),
            'github': float(github),
            'views': float(views),
            'conn': float(conn)
        })
    return rows


def normalize(vals):
    lo = min(vals); hi = max(vals)
    if hi==lo: return [0.0]*len(vals)
    return [(v-lo)/(hi-lo) for v in vals]


def make_preds_with_params(rows, params, seed=42):
    # prepare numpy arrays
    feats = ['completeness','years','skill_count','avg_skill_prof','recruiter','github','views','conn']
    X = np.vstack([[r[f] for f in feats] for r in rows])
    # normalize each column
    Xn = np.column_stack([normalize(X[:,i]) for i in range(X.shape[1])])
    # sample train indices
    n = Xn.shape[0]
    sample_idx = np.random.RandomState(seed).choice(n, size=min(25000,n), replace=False)
    X_train = Xn[sample_idx]
    # pseudo-target: weighted sum heuristic
    target = (0.3*Xn[:,0] + 0.2*Xn[:,4] + 0.2*Xn[:,1] + 0.15*Xn[:,2] + 0.15*Xn[:,3])
    y_train = target[sample_idx]

    dtrain = lgb.Dataset(X_train, label=y_train)
    model = lgb.train(params, dtrain, num_boost_round=200, callbacks=[lgb.log_evaluation(period=0)])
    preds = model.predict(Xn)
    return preds


def proxy_metric(rows, scores):
    # compute average completeness (original scale) and recruiter in top-100
    paired = list(zip([r['candidate_id'] for r in rows], scores, [r['completeness'] for r in rows], [r['recruiter'] for r in rows]))
    # round scores to 4 decimals and sort
    paired_sorted = sorted(paired, key=lambda x: (-round(x[1],4), x[0]))
    top = paired_sorted[:100]
    avg_compl = float(np.mean([t[2] for t in top]))
    avg_recr = float(np.mean([t[3] for t in top]))
    return 0.6*(avg_compl/100.0) + 0.4*avg_recr


def read_submission(path):
    import csv
    rows = {}
    if not Path(path).exists():
        return rows
    with open(path, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows[row['candidate_id']] = float(row['score'])
    return rows


def main():
    candidates = list(load_candidates(Path(r"c:\Hackathon\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl")))
    rows = features_from_candidates(candidates)

    # baseline model and previous model scores
    base_scores = read_submission(BASE)
    model_scores = read_submission(MODEL)

    best = None
    best_metric = -1
    best_preds = None
    # random search space
    for t in range(40):
        params = {
            'objective':'regression','metric':'l1','learning_rate':random.choice([0.01,0.03,0.05,0.08]),
            'num_leaves':random.choice([31,63,127]), 'min_data_in_leaf':random.choice([10,20,50]),
            'feature_fraction':random.choice([0.6,0.8,1.0]), 'bagging_fraction':random.choice([0.6,0.8,1.0]),
            'bagging_freq':1, 'verbosity':-1, 'seed':42+t
        }
        preds = make_preds_with_params(rows, params, seed=42+t)
        # ensemble with baseline & old model if available
        ensembled = []
        for i,r in enumerate(rows):
            cid = r['candidate_id']
            parts = [preds[i]]
            if cid in base_scores: parts.append(base_scores[cid])
            if cid in model_scores: parts.append(model_scores[cid])
            ensembled.append(np.mean(parts))

        metric = proxy_metric(rows, ensembled)
        if metric > best_metric:
            best_metric = metric
            best_preds = ensembled
            best = params
        if (t+1)%10==0:
            print(f"Trial {t+1}/40 best_metric={best_metric:.6f}")

    print("Best params:", best)
    print("Best metric:", best_metric)

    # write submission_final.csv using rounded score order
    paired = list(zip([r['candidate_id'] for r in rows], best_preds))
    paired_sorted = sorted(paired, key=lambda x:(-round(x[1],4), x[0]))
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['candidate_id','rank','score','reasoning'])
        for i,(cid,score) in enumerate(paired_sorted[:100], start=1):
            w.writerow([cid, i, f"{round(score,4):.4f}", 'Final ensemble'])

    # package final artifacts
    with zipfile.ZipFile(PKG, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(OUT, OUT.name)
        if BASE.exists(): z.write(BASE, BASE.name)
        if MODEL.exists(): z.write(MODEL, MODEL.name)
        z.write(Path('c:\Hackathon\hackathon_solution\README_FINAL.md'), 'README_FINAL.md')

    print(f"Wrote final submission: {OUT}")
    print(f"Created package: {PKG}")


if __name__ == '__main__':
    main()
