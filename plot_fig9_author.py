"""Plot published Starburst Fig 9 *from author's pickle log* (not digitized/invented points).
Run only on trusted logs: pickle can execute arbitrary Python code.
"""
import argparse
import csv
import pickle
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
sys.path.insert(0, str(Path.home()/'starburst')) # optional original modules for unpickling
LABELS={
    ('constant',-1,-1):'Constant-Wait',
    ('linear_runtime',-1,-1):'Runtime-Wait',
    ('linear_cost',-1,-1):'Compute-Wait',
    ('linear_capacity',-1,-1):'Resource-Wait',
    ('zero',-1,-1):'No-Wait',
    ('linear_capacity',0.25,3):'Star-Wait',
}
COLORS={'No-Wait':'tab:blue','Constant-Wait':'tab:orange',
    'Compute-Wait':'tab:red','Star-Wait':'tab:purple',
    'Runtime-Wait':'tab:green','Resource-Wait':'tab:brown'}
ORDER=['No-Wait','Constant-Wait','Runtime-Wait','Resource-Wait','Star-Wait','Compute-Wait']

def flatten(d):
    """Equivalent to skyburst.utils.flatten_dict(..., preserve_name=True)."""
    out={}
    for k,v in d.items():
        if isinstance(v,dict): out.update(flatten(v))
        else: out[k]=v
    return out

def scalar(v):
    if hasattr(v,'item') and not isinstance(v,(list,tuple,dict)):
        try: return v.item()
        except (ValueError,AttributeError): pass
    return v

def summarize(raw):
    results=[]
    for item in raw:
        d=flatten(item)
        policy=str(scalar(d.get('waiting_policy','')))
        if policy not in {'zero','constant','linear_runtime','linear_cost','linear_capacity'}:
            continue
        th=float(scalar(d.get('long_job_thres',-1)))
        ratio=float(scalar(d.get('preempt_cloud_ratio',-1)))
        key=(policy,th,ratio)
        if key not in LABELS: continue
        arrival=float(scalar(d['arrival_rate']))
        gpu=np.asarray(d['num_gpus'],dtype=float)
        runtime=np.asarray(d['runtime'],dtype=float)
        if gpu.size != runtime.size or gpu.size==0:
            raise ValueError('Job arrays missing or unequal sizes in author log')
        mean_compute=float(np.mean(gpu*runtime))
        capacity=float(scalar(d['cluster_size']))*float(scalar(d['gpus_per_node']))
        row=dict(policy=LABELS[key], arrival_rate=arrival,
                 system_load=arrival*mean_compute/capacity,
                 total_cloud_cost=float(scalar(d['total_cloud_cost'])),
                 avg_jct=float(scalar(d['avg_jct'])),
                 cluster_utilization=float(scalar(d['cluster_utilization'])))
        results.append(row)
    if not results: raise ValueError('No figure9 policy configurations found; check log source/schema')
    return results

def plot(rows):
    baselines={r['arrival_rate']:r['total_cloud_cost'] for r in rows if r['policy']=='No-Wait'}
    if not baselines: raise ValueError('Missing No-Wait baseline')
    for r in rows:
        if r['arrival_rate'] not in baselines:
            raise ValueError(f"Missing baseline for arrival={r['arrival_rate']}")
        r['cost_savings_usd']=2.5*(baselines[r['arrival_rate']]-r['total_cloud_cost'])
    peak=max(r['cost_savings_usd'] for r in rows)
    if peak<=0: raise ValueError('No positive savings; cannot normalize as in author notebook')
    for r in rows: r['normalized_cost_savings']=r['cost_savings_usd']/peak
    fig,axes=plt.subplots(1,2,figsize=(11,4),sharex=True)
    for label in ORDER:
        rr=sorted((r for r in rows if r['policy']==label),key=lambda x:x['system_load'])
        if not rr: continue
        if label!='No-Wait':
            axes[0].plot([r['system_load'] for r in rr],
                         [r['normalized_cost_savings'] for r in rr],'-o',ms=3,
                         lw=1.5,color=COLORS[label],label=label)
        axes[1].plot([r['system_load'] for r in rr],
                     [r['avg_jct'] for r in rr],'-o',ms=3,lw=1.5,
                     color=COLORS[label],label=label)
    axes[0].set(ylabel='Normalized Cost Savings ($)',xlabel='System Load (s)')
    axes[1].set(ylabel='Avg. JCT (hr)',xlabel='System Load (s)')
    for ax in axes:
        ax.grid(alpha=.4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    handles,labels=axes[1].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=3,loc='upper center',bbox_to_anchor=(.5,1.08))
    fig.tight_layout(rect=[0,0,1,.87])
    output=ROOT/'results'
    output.mkdir(exist_ok=True)
    fig.savefig(output/'figure9_author.png',dpi=200,bbox_inches='tight')
    fig.savefig(output/'figure9_author.pdf',bbox_inches='tight')
    plt.close(fig)
    with (output/'figure9_author.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader();writer.writerows(sorted(rows,key=lambda r:(r['policy'],r['arrival_rate'])))
    print(f"Generated {output/'figure9_author.png'}, .pdf and .csv from {len(rows)} author log results")
    print('Using official notebook formula: (cost baseline - policy cost) * 2.5 / max difference')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--log',type=Path,default=ROOT/'data'/'ablate_waiting_policies.log')
    args=parser.parse_args()
    path=args.log.expanduser()
    if not path.is_file():
        raise SystemExit(f"Missing author log: {path}\nRun ./download_author_log.sh, or copy your original log to data/.")
    # WARNING: pickle files must be from trusted official repository/bucket only.
    with path.open('rb') as f: raw=pickle.load(f)
    rows=summarize(raw)
    plot(rows)
if __name__=='__main__': main()
