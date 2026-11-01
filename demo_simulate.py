"""Demonstration only: synthetic tiny sample. Never use as published Figure 9 data."""
import argparse
import csv
from pathlib import Path
from src.policies import POLICIES
from src.simulator import generate_jobs, run

p=argparse.ArgumentParser()
p.add_argument('--jobs', type=int, default=1500)
p.add_argument('--capacity', type=int, default=64)
a=p.parse_args()
Path('results').mkdir(exist_ok=True)
rows=[]
for policy in POLICIES:
    jobs=generate_jobs(a.jobs, seed=1994)
    r=run(jobs,policy,capacity=a.capacity)
    rows.append(r)
    print(r)
with open('results/demo_not_published.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print('Saved results/demo_not_published.csv')
