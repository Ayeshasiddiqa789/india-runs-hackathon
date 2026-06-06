#!/usr/bin/env python3
"""Ensemble baseline and model submissions, produce final CSV and demo artifacts, and package for submission.

Writes:
- c:\Hackathon\submission_ensemble.csv
- c:\Hackathon\top20.json
- c:\Hackathon\hackathon_solution\submission_package.zip
"""
from pathlib import Path
import csv
import json
import zipfile


BASE = Path(r"c:\Hackathon\submission.csv")
MODEL = Path(r"c:\Hackathon\submission_model.csv")
OUT = Path(r"c:\Hackathon\submission_ensemble.csv")
TOP20 = Path(r"c:\Hackathon\top20.json")
PKG = Path(r"c:\Hackathon\hackathon_solution\submission_package.zip")


def read_submission(p: Path):
    rows = []
    if not p.exists():
        return rows
    with open(p, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({
                'candidate_id': row['candidate_id'],
                'score': float(row['score']),
                'rank': int(row['rank']),
                'reasoning': row.get('reasoning','')
            })
    return rows


def main():
    base = read_submission(BASE)
    model = read_submission(MODEL)

    scores = {}
    for r in base:
        scores.setdefault(r['candidate_id'], []).append(r['score'])
    for r in model:
        scores.setdefault(r['candidate_id'], []).append(r['score'])

    averaged = []
    for cid, vals in scores.items():
        avg = sum(vals)/len(vals)
        averaged.append((cid, round(avg,4)))

    # sort by rounded score desc, tie-break candidate_id
    averaged.sort(key=lambda x: (-x[1], x[0]))

    # write top 100
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['candidate_id','rank','score','reasoning'])
        for i, (cid, score) in enumerate(averaged[:100], start=1):
            w.writerow([cid, i, f"{score:.4f}", "Ensembled score (avg of baseline+model)"])

    # top20 json for demo
    top20 = [{'candidate_id': cid, 'score': f"{score:.4f}", 'rank': i+1} for i, (cid, score) in enumerate(averaged[:20])]
    with open(TOP20, 'w', encoding='utf-8') as f:
        json.dump(top20, f, indent=2)

    # package: include scripts, README_FINAL, and submissions
    with zipfile.ZipFile(PKG, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(OUT, OUT.name)
        if BASE.exists():
            z.write(BASE, BASE.name)
        if MODEL.exists():
            z.write(MODEL, MODEL.name)
        z.write(Path(__file__), 'ensemble_and_package.py')
        readme = Path('c:\Hackathon\hackathon_solution\README_FINAL.md')
        if readme.exists():
            z.write(readme, 'README_FINAL.md')

    print(f"Wrote ensemble: {OUT}")
    print(f"Wrote demo JSON: {TOP20}")
    print(f"Created package: {PKG}")


if __name__ == '__main__':
    main()
