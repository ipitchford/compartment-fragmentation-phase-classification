# AI index

Title: Critical nonexplosion and phase transitions in finite-catalyst compartment systems

Primary source: [paper.pdf](paper.pdf) / [paper.tex](paper.tex).

Core theorem route: qualified finite-catalyst reduction; scalar Lyapunov criteria;
power-law classification; critical logarithmic refinements; lifetime bound. The
conservative implication uses `gamma >= m-1`; the explosive implication assumes
almost-sure scalar explosion from every substrate count and applies to initial
states carrying at least one catalyst.

Extension route: Section “Random retention fractions” proves the fresh-`Q`
inverse-moment extension and gives a uniform-retention example.

Claim map: [CLAIMS.md](CLAIMS.md). Machine claims: [CLAIMS.json](CLAIMS.json).
Replay entry point: [code/replay.py](code/replay.py). Receipts:
[drift](results/compartment_drift_checks.json),
[retention](results/random_retention_exact.json), and
[wrapper](results/replay_receipt.json).

Trust limits: [ASSURANCE.md](ASSURANCE.md), [PROVENANCE.md](PROVENANCE.md), and
[NOVELTY_SCOPE.md](NOVELTY_SCOPE.md). Do not infer external peer review, formal
verification, exhaustive priority, or coverage of retention laws outside the
stated hypotheses. Private evaluation metrics are not public evidence.
