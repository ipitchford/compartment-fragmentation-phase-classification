#!/usr/bin/env python3
"""Exact finite arithmetic checks for the random-retention modelling example.

Uses only the Python standard library. Seven mixed-binomial probability rows
are checked with fractions.Fraction. Positive exponential Taylor series and
a geometric remainder bound certify the chosen strict logarithmic interval.
These checks do not prove any stochastic or asymptotic theorem.
"""
from fractions import Fraction as Q
from math import comb, factorial
from pathlib import Path
import argparse
import json
import sys


class VerificationError(RuntimeError):
    """Raised when an exact finite check fails."""


def require(condition, message):
    """Fail closed even when Python assertions are optimized away."""
    if not condition:
        raise VerificationError(message)


def binomial_row(s, q):
    """Return the exact probabilities of Bin(s, q), ordered from 0 to s."""
    return [Q(comb(s, k)) * q**k * (1-q)**(s-k)
            for k in range(s+1)]


def check_mixture_row(s):
    first = binomial_row(s, Q(1, 4))
    second = binomial_row(s, Q(3, 4))
    probabilities = [(a+b)/2 for a, b in zip(first, second)]
    total = sum(probabilities, Q(0))
    mean = sum((k*p for k, p in enumerate(probabilities)), Q(0))
    variance = sum(((Q(k)-mean)**2*p
                    for k, p in enumerate(probabilities)), Q(0))
    expected_mean = Q(s, 2)
    expected_variance = Q(s*s+3*s, 16)
    require(all(p >= 0 for p in probabilities), f"negative probability in row {s}")
    require(total == 1, f"row {s} does not normalize: {total}")
    require(mean == expected_mean, f"row {s} mean mismatch: {mean}")
    require(variance == expected_variance, f"row {s} variance mismatch: {variance}")
    return {
        's': s,
        'probabilities_k_0_through_s': [str(p) for p in probabilities],
        'normalisation': str(total),
        'mean': str(mean),
        'expected_mean': str(expected_mean),
        'variance': str(variance),
        'expected_variance': str(expected_variance),
    }


def exponential_bounds(x, degree):
    """Give rational lower and upper bounds for exp(x), for positive x.

    Let S_N=sum_{k=0}^N x^k/k! and t_{N+1}=x^(N+1)/(N+1)!.
    For every subsequent term the ratio to its predecessor is at most
    r=x/(N+2). If r<1, positivity and the geometric series give

        S_N < exp(x) <= S_N + t_{N+1}/(1-r).

    All quantities computed here are rational. No floating-point exp or log
    evaluation is used to establish either inequality.
    """
    x = Q(x)
    require(x > 0 and degree >= 0, "invalid exponential-bound parameters")
    terms = [Q(1)]
    for k in range(1, degree+1):
        terms.append(terms[-1]*x/k)
    lower = sum(terms, Q(0))
    first_omitted = terms[-1]*x/(degree+1)
    ratio_upper = x/(degree+2)
    require(0 < ratio_upper < 1, "geometric remainder ratio is not in (0,1)")
    remainder_upper = first_omitted/(1-ratio_upper)
    upper = lower+remainder_upper
    return lower, upper, {
        'argument': str(x),
        'taylor_degree': degree,
        'included_terms': [str(term) for term in terms],
        'strict_lower_bound': str(lower),
        'first_omitted_term': str(first_omitted),
        'subsequent_term_ratio_upper_bound': str(ratio_upper),
        'geometric_remainder_upper_bound': str(remainder_upper),
        'upper_bound': str(upper),
    }


def uniform_beta_binomial_row(s):
    """Check Q uniform on (0,1), Y|Q~Bin(s,Q), so Y is uniform."""
    # Integrating the conditional binomial mass over q in (0,1) gives
    #   C(s,k) * B(k+1,s-k+1)
    # = C(s,k) * k! * (s-k)! / (s+1)! = 1/(s+1).
    probabilities = [
        Q(comb(s, k) * factorial(k) * factorial(s - k), factorial(s + 1))
        for k in range(s + 1)
    ]
    require(
        all(p == Q(1, s + 1) for p in probabilities),
        f"uniform-retention beta integral failed for row {s}",
    )
    total = sum(probabilities, Q(0))
    mean = sum((Q(k) * p for k, p in enumerate(probabilities)), Q(0))
    variance = sum(((Q(k) - mean) ** 2 * p for k, p in enumerate(probabilities)), Q(0))
    require(total == 1, f"uniform-retention row {s} does not normalize")
    require(mean == Q(s, 2), f"uniform-retention row {s} mean mismatch")
    require(variance == Q(s * (s + 2), 12), f"uniform-retention row {s} variance mismatch")
    return {
        "s": s,
        "probability_each_state": str(Q(1, s + 1)),
        "beta_integral_identity": "C(s,k) k! (s-k)!/(s+1)! = 1/(s+1)",
        "mean": str(mean),
        "variance": str(variance),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-control", choices=("mixture-variance", "uniform-row"))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.negative_control == "mixture-variance":
        row = check_mixture_row(6)
        require(row["variance"] == str(Q(6 * 6 + 3 * 6, 17)), "deliberately false mixture variance divisor")
    if args.negative_control == "uniform-row":
        row = uniform_beta_binomial_row(4)
        require(row["probability_each_state"] == str(Q(1, 6)), "deliberately false uniform row")

    states = (0, 1, 2, 3, 4, 8, 16)
    rows = [check_mixture_row(s) for s in states]

    lower, _, lower_certificate = exponential_bounds(Q(3, 4), 2)
    require(lower > 2, "failed to certify exp(3/4) > 2")
    lower_certificate.update({
        'certified_inequality': 'exp(3/4) > 2',
        'rational_margin': str(lower-2),
        'logarithmic_consequence': 'log(2) < 3/4',
    })

    _, upper, upper_certificate = exponential_bounds(Q(3, 2), 4)
    require(upper < Q(16, 3), "failed to certify exp(3/2) < 16/3")
    upper_certificate.update({
        'certified_inequality': 'exp(3/2) < 16/3',
        'rational_margin': str(Q(16, 3)-upper),
        'logarithmic_consequence': '3/4 < (1/2)*log(16/3)',
    })

    uniform_rows = [uniform_beta_binomial_row(s) for s in range(33)]

    report = {
        'arithmetic': 'Python fractions.Fraction; exact rational arithmetic',
        'validation': 'explicit VerificationError checks; active under python -O',
        'python_optimization_flag': sys.flags.optimize,
        'interpretation': (
            'Finite probability-row and exponential-series checks for the '
            'modelling example; not a proof of any stochastic or asymptotic theorem.'
        ),
        'retention_fractions': ['1/4', '3/4'],
        'mixture_weights': ['1/2', '1/2'],
        'states_checked': list(states),
        'mixture_rows_checked': len(rows),
        'probability_entries_checked': sum(s+1 for s in states),
        'normalisation_checks': len(rows),
        'mean_checks': len(rows),
        'variance_checks': len(rows),
        'exponential_inequalities_checked': 2,
        'strict_logarithmic_interval': 'log(2) < 3/4 < (1/2)*log(16/3)',
        'logarithmic_interval_certified': True,
        'all_explicit_checks_passed': True,
        'uniform_retention_example': {
            'law': 'Q uniform on (0,1), conditional Y~Bin(s,Q)',
            'states_checked': [0, 32],
            'rows_checked': len(uniform_rows),
            'identity': 'P(Y=j)=1/(s+1); mean=s/2; variance=s(s+2)/12',
            'rows': uniform_rows,
        },
        'rows': rows,
        'exponential_series_bound': (
            'For x>0, S_N=sum(x^k/k!, k=0..N) is a strict lower bound. '
            'If r=x/(N+2)<1, the omitted positive terms have successive '
            'ratios at most r, so their sum is at most '
            '[x^(N+1)/(N+1)!]/(1-r).'
        ),
        'exponential_certificates': [lower_certificate, upper_certificate],
    }
    out = args.output or (Path(__file__).resolve().parents[1]/'results'/'random_retention_exact.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2)+'\n')
    summary_keys = (
        'arithmetic', 'interpretation', 'mixture_rows_checked',
        'probability_entries_checked', 'normalisation_checks', 'mean_checks',
        'variance_checks', 'exponential_inequalities_checked',
        'strict_logarithmic_interval', 'logarithmic_interval_certified',
        'all_explicit_checks_passed', 'uniform_retention_example',
        'exponential_certificates',
    )
    print(json.dumps({key: report[key] for key in summary_keys}, indent=2))


if __name__ == '__main__':
    main()
