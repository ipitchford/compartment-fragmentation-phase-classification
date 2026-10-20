# Assurance boundaries

The universal stochastic statements are analytic proofs. Deterministic binary64
sanity checks cover representative generator values, Jensen inequalities and
binomial moments. Separate exact-rational checks cover mixed-binomial rows,
rational exponential bounds and the uniform beta-binomial identity. Both remain
active under optimized Python and include deliberate negative controls.

The random-retention extension requires a fresh independent `Q` in `(0,1]`,
positive probability of loss, one finite inverse moment, and uniform conditional
mean and variance bounds. It does not cover an atom at zero, state-dependent or
history-dependent retention laws, correlated compartments, or arbitrary heavy
lower tails. Finite checks do not prove explosion, conservativity, novelty or
external acceptance. AI review is not independent human peer review.
