# Replay record

On 20 October 2026, `python3 -B code/replay.py` passed. The wrapper launched each
validator in ordinary and optimized modes, required reported optimization flags
0 and 1, and compared receipts after removing only that flag.

The drift validator checks 21 Jensen inequalities, 48 generator values and 12
binomial moment calculations through substrate count 100,000. The retention
validator checks seven exact mixed-binomial rows (41 probability entries), two
rational exponential-series inequalities, and 33 exact uniform beta-binomial
rows derived from `C(s,k) k! (s-k)!/(s+1)!`.

Four negative controls—Jensen, variance, mixture variance and uniform row—were
required to raise `VerificationError` in both modes. The public JSON receipts are
under `results/`. These checks support finite identities only; the manuscript's
analytic proof establishes the stochastic classification.
