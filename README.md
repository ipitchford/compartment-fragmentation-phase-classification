# Critical nonexplosion and phase transitions in finite-catalyst compartment systems

Anonymous. Version 1.0.0-candidate, revised 20 October 2026.

Version DOI: [10.5281/zenodo.23505123](https://doi.org/10.5281/zenodo.23505123).

This paper gives a complete phase classification for a stochastic population of
compartments whose substrate grows and is redistributed when a compartment
fragments. A qualified reduction transfers conservativity or almost-sure
explosion between one-catalyst lineages and finite catalyst populations. Sharp power-law
thresholds for production and fragmentation, critical logarithmic regimes and finite expected explosion times are
then obtained by explicit Lyapunov arguments.

The revision extends the classification from a fixed retained fraction to a
fresh random fraction `Q` in `(0,1]`, assuming one finite inverse moment and
uniform conditional first- and second-moment bounds. A uniform-retention example
shows that equal mean retention does not determine the phase boundary.

## Start here

- `paper.pdf` and `paper.tex`: complete theorem statements and proofs.
- `CLAIMS.md` / `CLAIMS.json`: exact claim-to-evidence boundaries.
- `code/replay.py`: ordinary and optimized finite checks with deliberate failures.
- `results/`: regenerated public receipts.
- `AI_INDEX.md`: agent-oriented navigation and non-claims.
- `ASSURANCE.md`, `PROVENANCE.md`, `NOVELTY_SCOPE.md`: trust and priority limits.

## Replay

```sh
python3 -B code/replay.py
```

The wrapper runs both ordinary and optimized Python, verifies their optimization
flags, compares semantic receipts, and requires four deliberate negative controls
to raise `VerificationError` in both modes. The finite checks support the examples
and algebra; they do not prove the asymptotic stochastic theorems.

Text and generated data: CC0-1.0. Original code: MIT.
