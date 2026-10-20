#!/usr/bin/env python3
"""Deterministic finite-state sanity checks for the compartment proofs.

Uses only the Python standard library. These floating-point checks validate
representative generator calculations and their signs; they do not prove
nonexplosion, almost-sure explosion, or any asymptotic statement.
"""
import json
import math
from pathlib import Path
import argparse
import sys


class VerificationError(RuntimeError):
    """Raised when a finite arithmetic check fails."""


def require(condition, message):
    """Fail closed under ordinary and optimized Python execution."""
    if not condition:
        raise VerificationError(message)


def binomial_weights(n, p):
    """Normalised full-support probabilities, using a mode-centred recurrence."""
    mode = min(n, int((n + 1) * p))
    weights = [0.0] * (n + 1)
    weights[mode] = 1.0
    for j in range(mode, 0, -1):
        weights[j - 1] = weights[j] * j * (1 - p) / ((n - j + 1) * p)
    for j in range(mode, n):
        weights[j + 1] = weights[j] * (n - j) * p / ((j + 1) * (1 - p))
    total = math.fsum(weights)
    return [w / total for w in weights]


def expectation(weights, function):
    return math.fsum(w * function(j) for j, w in enumerate(weights) if w)


def logarithmic_test(kind, s, c=20.0, r=0.2):
    y = math.log(s + c)
    if kind == 'double_log':
        return math.log(y)
    if kind == 'triple_log':
        return math.log(math.log(y))
    if kind == 'log_power':
        return y ** (-r)
    raise ValueError(kind)


def upward_difference(kind, s, c=20.0, r=0.2):
    # Evaluate tiny positive-step differences with log1p/expm1.
    y = math.log(s + c)
    dy = math.log1p(1 / (s + c))
    dlogy = math.log1p(dy / y)
    if kind == 'double_log':
        return dlogy
    if kind == 'triple_log':
        return math.log1p(dlogy / math.log(y))
    if kind == 'log_power':
        return y ** (-r) * math.expm1(-r * dlogy)
    raise ValueError(kind)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", choices=("jensen", "variance"))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.negative_control == "jensen":
        weights = binomial_weights(10, 0.5)
        observed = expectation(weights, lambda j: math.log(j) if j else -2.0)
        require(observed <= -100.0, "deliberately false Jensen bound")
    if args.negative_control == "variance":
        weights = binomial_weights(8, 0.5)
        mean = expectation(weights, float)
        variance = expectation(weights, lambda j: (j - mean) ** 2)
        require(abs(variance - 8 / 17) < 1e-15, "deliberately false variance divisor")

    rows = []
    jensen_rows = []
    moment_errors = []
    for p in (0.3, 0.5, 0.8):
        ell = math.log(1 / p)
        for n in (1, 2, 5, 10, 50, 100, 1000):
            weights = binomial_weights(n, p)
            def g(j):
                return math.log(j) if j else math.log(p) - 1
            eg = expectation(weights, g)
            bound = math.log(p * n)
            require(eg <= bound + 2e-13, f"Jensen check failed for p={p}, n={n}")
            jensen_rows.append(dict(p=p, n=n, expected_g=eg,
                                    jensen_upper=bound, margin=bound-eg))
        sigma2 = ell * ell
        scenarios = [
            ('polynomial_perturbation', 'double_log', 0.0, 100.0,
             -sigma2 / 2),
            ('secondary_subcritical', 'double_log', 0.0, 0.0,
             -sigma2 / 2),
            ('secondary_equality', 'triple_log', sigma2 / 2, 0.0,
             -sigma2 / 2),
            ('secondary_supercritical', 'log_power', sigma2, 0.0,
             0.2 * (sigma2 * 1.2 / 2 - sigma2)),
        ]
        for n in (100, 1000, 10000, 100000):
            weights = binomial_weights(n, p)
            mean = expectation(weights, float)
            variance = expectation(weights, lambda j: (j - mean) ** 2)
            mean_error = abs(mean - n*p) / max(1.0, n*p)
            var_error = abs(variance - n*p*(1-p)) / max(1.0, n*p*(1-p))
            require(
                mean_error < 1e-12 and var_error < 1e-12,
                f"binomial moment check failed for p={p}, n={n}",
            )
            moment_errors.append(dict(p=p,n=n,mean_relative_error=mean_error,
                                      variance_relative_error=var_error))
            for name, kind, beta, polynomial, expected_limit in scenarios:
                # m=2, kappa=1, D=0, alpha=ell, b=1.
                birth = 1 + n*n*(ell + beta/math.log(n)) + polynomial*n
                fragment = float(n)
                value = logarithmic_test(kind, n)
                collapse_delta = expectation(weights,
                    lambda j: logarithmic_test(kind,j)-value)
                drift = birth*upward_difference(kind,n)+fragment*collapse_delta
                y = math.log(n+20.0)
                if kind == 'double_log':
                    normalisation = n/y**2
                elif kind == 'triple_log':
                    normalisation = n/(y**2*math.log(y)**2)
                else:
                    normalisation = n/y**2.2
                rows.append(dict(scenario=name,p=p,n=n,test=kind,drift=drift,
                    normalised_drift=drift/normalisation,
                    predicted_limit=expected_limit))

    # This is an observed finite-scale sign check, not a certified threshold.
    high_rows = [row for row in rows if row['n'] == 100000]
    require(all(row['drift'] < 0 for row in high_rows), "high-state drift sign check failed")
    report = dict(
        arithmetic='Python binary64 floats; deterministic full-support binomial sums',
        interpretation='Finite-scale sanity checks only; the manuscript supplies the proof.',
        validation='explicit VerificationError checks; active under python -O',
        python_optimization_flag=sys.flags.optimize,
        jensen_cases=len(jensen_rows), generator_cases=len(rows),
        moment_cases=len(moment_errors), highest_state_checked=100000,
        all_explicit_checks_passed=True,
        high_state_results=high_rows, generator_results=rows,
        jensen_results=jensen_rows, binomial_moment_errors=moment_errors)
    out=args.output or (Path(__file__).resolve().parents[1]/'results'/'compartment_drift_checks.json')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in (
        'interpretation','jensen_cases','generator_cases','moment_cases',
        'highest_state_checked','all_explicit_checks_passed','high_state_results')},indent=2))


if __name__ == '__main__':
    main()
