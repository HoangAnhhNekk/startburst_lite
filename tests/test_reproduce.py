import unittest
from src.policies import Job, max_wait
from src.simulator import generate_jobs, run

class TestPolicies(unittest.TestCase):
    def test_wait_formulas(self):
        j=Job(arrival=0,runtime=2,gpus=4,identifier=0)
        self.assertEqual(max_wait(j,'No-Wait'),0)
        self.assertAlmostEqual(max_wait(j,'Constant-Wait'),.454)
        self.assertAlmostEqual(max_wait(j,'Runtime-Wait'),.5)
        self.assertAlmostEqual(max_wait(j,'Resource-Wait'),.936)
        self.assertAlmostEqual(max_wait(j,'Compute-Wait'),.32)
        self.assertEqual(max_wait(j,'Star-Wait'),0)
        self.assertAlmostEqual(max_wait(j,'Star-Wait',preempted=True),.936)
    def test_small_simulation_completes_all_jobs(self):
        jobs=generate_jobs(n=100,seed=1994)
        for name in ('No-Wait','Constant-Wait','Runtime-Wait','Resource-Wait','Compute-Wait','Star-Wait'):
            result=run(jobs,policy=name,capacity=64)
            self.assertEqual(result['jobs'],100)
            self.assertGreater(result['avg_jct'],0)
            self.assertGreaterEqual(result['cluster_utilization'],0)
            self.assertLessEqual(result['cluster_utilization'],1.000001)

if __name__=='__main__': unittest.main()
