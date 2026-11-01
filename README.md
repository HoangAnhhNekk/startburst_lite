# Starburst Figure 9 – lightweight reproduction for Ubuntu

## What this project does

**Mode A (published original numbers):** plots Figure 9 using the *authors' previously computed simulation log*, not made-up or hand-traced numbers. Running the full 300,000-job sweep is **not required**. The published log is **NOT included** in this ZIP because its bytes could not be fetched/verified here; it must be downloaded from the authors' public storage. This package is not claiming to have recomputed the paper's numbers.

**Mode B (mini simulator):** an educational, single-process, non-identical implementation of Starburst's maximum waiting-time formulas, cloud timeout, out-of-order backfill, and simple Star-Wait preemption. Small synthetic input for understanding the algorithms; output does **NOT** constitute reproduction of paper results.

## Ubuntu quick start (Mode A)

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip curl unzip
unzip starburst_fig9_light.zip
cd starburst_fig9_light
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./download_author_log.sh
python plot_fig9_author.py
```

Result files:

- `results/figure9_author.png`
- `results/figure9_author.pdf`
- `results/figure9_author.csv`

If direct download fails due to blocked public-object URL, use Google Cloud CLI (gsutil) or copy the original log already downloaded by the official setup:

```bash
mkdir -p data
cp ~/logs/ablate_waiting_policies.log data/
# or
# gsutil cp gs://starburst_bucket/logs/ablate_waiting_policies.log data/
python plot_fig9_author.py
```

The author stores data at `gs://starburst_bucket/logs/ablate_waiting_policies.log`. Their reference plotting notebook is `skyburst/notebooks/fig9_ablate_waiting_policy.ipynb` in https://github.com/michaelzhiluo/starburst.

### Important about Python pickle

Only unpickle author-provided, trusted files. Python pickle loading is not safe for untrusted files. If the log was generated with custom `skyburst` objects, clone/keep original `~/starburst` on the machine; this script adds it to Python path.

### Figure 9 parameters from official `simulator_scripts/fig9.sh`

- dataset: `helios_gen` (synthetic Helios, NOT raw Venus)
- 300,000 jobs, 64 nodes, 48 CPUs/node, seed 1994
- arrival rates: `8 12 16 20 24 25 26 27 28 32 34 36 40 44 48 52 56 60 64 68 72 76 80 84 88 92`
- policies: `zero-1 constant-0.454 linear_cost-0.04 linear_runtime-0.25 linear_capacity-0.234`
- preemption ratio: `-1 3`, long-job threshold: `-1 0.25`, out-of-order `--loop 1`
- official parameter filter: `ablate_waiting_policy`

The published notebook computes `s = arrival_rate * mean(num_gpus * runtime) / (cluster_size * gpus_per_node)`; and Figure 9's **left axis is normalized absolute cost savings**, NOT Cost Savings (%). The official notebook normalizes `(No-Wait cost - policy cost)*2.5` by the maximum difference across all policies and arrivals. Right axis is average JCT in hours.

The paper: Starburst, USENIX ATC 2024, Figure 9, page 47 of proceedings / PDF page 12.

## Ubuntu quick start (Mode B – only illustrative)

```bash
python demo_simulate.py --jobs 1500 --capacity 64
```

Outputs `results/demo_not_published.csv` only. The pedagogical simulator intentionally omits multinode binpacking, resource-specific CPU accounting, several cloud-model details and author-equivalent preemption; it is *not numerically equivalent* to the original simulator.

## Where to look

```text
starburst_fig9_light/
├── README.md
├── requirements.txt
├── download_author_log.sh
├── plot_fig9_author.py        # Published author's log -> paper Figure 9 chart & CSV
├── demo_simulate.py           # Educational mini-simulator
├── src/
│   ├── __init__.py
│   ├── policies.py            # No-Wait, Constant, Runtime, Resource, Compute, Star
│   └── simulator.py           # Discrete-event queue / cloud timeouts / OO
├── data/                      # Published .log goes here
├── results/                   # Outputs
└── reference/
    └── figure9_paper.png     # Crop of the user-supplied paper for visual comparison
```

## References

- Original repository: https://github.com/michaelzhiluo/starburst
- Exact Fig 9 experiment: https://github.com/michaelzhiluo/starburst/blob/main/simulator_scripts/fig9.sh
- Original Fig 9 plotting notebook: https://github.com/michaelzhiluo/starburst/blob/main/skyburst/notebooks/fig9_ablate_waiting_policy.ipynb
- Paper: https://www.usenix.org/system/files/atc24-luo.pdf

## One-command runner (Ubuntu)

After extracting, run `bash run_ubuntu.sh` to try author-log download and plot (internet required). If you already have the official log, copy it to `data/ablate_waiting_policies.log` first; it will not be downloaded again. Run `bash run_ubuntu.sh demo 1500 64` for a tiny demonstrator without any author data download. Test the learning simulator using `python -m unittest discover -s tests -v` after activating `.venv`.

**Troubleshooting:** If ChatGPT file download fails, the source project can alternatively be reconstructed from the source files shown in chat. If Google Cloud returns 403/404 or times out, this project cannot independently reproduce original author numbers; it will never replace them with invented values. The image in `reference/` is an excerpt from the supplied PDF, not an output from the simulator.
