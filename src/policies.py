"""Educational faithful policy formulas from Starburst ATC'24 §4.
This module is NOT an exact port of the author's discrete-event simulator.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Job:
    arrival: float
    runtime: float
    gpus: int
    identifier: int

# Figure 9 policy parameters: official fig9.sh.
POLICIES = {
    'No-Wait': ('zero', 0.0),
    'Constant-Wait': ('constant', 0.454),
    'Runtime-Wait': ('runtime', 0.25),
    'Resource-Wait': ('capacity', 0.234),
    'Compute-Wait': ('compute', 0.04),
    'Star-Wait': ('star', 0.234),
}

def max_wait(job: Job, policy: str, *, preempted: bool = False):
    kind, factor = POLICIES[policy]
    if kind == 'zero': return 0.0
    if kind == 'constant': return factor
    if kind == 'runtime': return factor * job.runtime
    if kind == 'capacity': return factor * job.gpus
    if kind == 'compute': return factor * job.runtime * job.gpus
    if kind == 'star': return factor * job.gpus if preempted else 0.0
    raise ValueError(policy)
