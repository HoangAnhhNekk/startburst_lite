"""Small discrete-event learning simulator, NOT an exact replication of author outputs.
Shows FIFO queue with out-of-order backfill, timeout to cloud, and Star-Wait requeue.
"""
import heapq
import itertools
import numpy as np
from .policies import Job, POLICIES, max_wait


def generate_jobs(n=1500, seed=1994, arrival_rate=4):
    rng = np.random.default_rng(seed)
    arrivals = np.cumsum(rng.exponential(1.0/arrival_rate, size=n))
    runtimes = np.maximum(0.02, rng.exponential(1.5, size=n))
    gpu_counts = rng.choice([1, 2, 4, 8, 16], size=n, p=[.45, .25, .17, .1, .03])
    return [Job(float(a), float(t), int(g), i) for i,(a,t,g) in enumerate(zip(arrivals,runtimes,gpu_counts))]


def run(jobs, policy='Compute-Wait', capacity=64, star_threshold=0.25):
    if policy not in POLICIES: raise ValueError(policy)
    # event order: time, priority, counter, type, job; complete before arrivals at ties
    serial = itertools.count()
    heap=[]
    def push(when, prio, typ, job): heapq.heappush(heap,(when,prio,next(serial),typ,job))
    for job in jobs: push(job.arrival,2,'arrive',job)
    queue=[]
    available=capacity
    result={}
    cloud_cost=0.0
    gpu_time=0.0
    last_time=0.0
    completed=0
    preempted=set()
    cloud_attempts={}
    while heap:
        now,_,__,kind,job=heapq.heappop(heap)
        gpu_time += (capacity-available)*(now-last_time)
        last_time=now
        if kind=='arrive' or kind=='retry':
            wait=max_wait(job,policy,preempted=job.identifier in preempted)
            queue.append((job,now+wait))
            push(now+wait,3,'timeout',job)
        elif kind=='timeout':
            if any(j.identifier==job.identifier for j,_ in queue):
                queue=[(j,d) for j,d in queue if j.identifier!=job.identifier]
                if policy=='Star-Wait' and job.identifier not in preempted and job.runtime>star_threshold:
                    preempted.add(job.identifier)
                    # lost work on cloud before preemption, then requeue once
                    cloud_cost += job.gpus*star_threshold
                    push(now+star_threshold,2,'retry',job)
                else:
                    cloud_cost += job.gpus*job.runtime
                    push(now+job.runtime,1,'cloud_done',job)
        elif kind=='private_done':
            available+=job.gpus
            result[job.identifier]=now-job.arrival
            completed+=1
        elif kind=='cloud_done':
            result[job.identifier]=now-job.arrival
            completed+=1
        # out-of-order: walk all waiting jobs, skipping those that cannot fit
        idx=0
        while idx<len(queue):
            nxt,deadline=queue[idx]
            if nxt.gpus<=available and nxt.gpus<=capacity:
                available-=nxt.gpus
                queue.pop(idx)
                push(now+nxt.runtime,0,'private_done',nxt)
            else:
                idx+=1
    return dict(policy=policy, avg_jct=sum(result.values())/len(jobs),
                total_cloud_cost=cloud_cost, cluster_utilization=gpu_time/(capacity*last_time),
                jobs=completed)
