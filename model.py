"""
A/B Testing & Causal Inference Toolkit

Assembled from your step-by-step solutions.
"""

import numpy as np

# Step 1 - standard_normal_cdf
import math
import numpy as np

def standard_normal_cdf(z):
    # TODO: return P(Z <= z) for a standard normal Z, supporting float or numpy array input
    root_two = math.sqrt(2)
    if np.isscalar(z):
        return 0.5*(1+math.erf(z/root_two))
    z = np.asarray(z, dtype=float)
    erf = np.vectorize(math.erf)
    return 0.5*(1+erf(z/root_two))
    pass

# Step 2 - standard_normal_ppf
import math
from scipy.special import erfinv

def standard_normal_ppf(p):
    """Return z such that Phi(z) = p for p in (0, 1)."""
    # TODO: implement a rational approximation to the inverse standard normal CDF
    root_two = math.sqrt(2)
    if np.isscalar(p):
        return root_two * erfinv(2*p - 1)
    
    p = np.asarray(p, dtype=float)
    return root_two * erfinv(2*p - 1)
    pass

# Step 3 - pooled_proportion
def pooled_proportion(successes_a, total_a, successes_b, total_b):
    # TODO: Compute the pooled success proportion across two groups for the null of equal rates.
    return ((successes_a+successes_b)/(total_a+total_b))
    pass

# Step 4 - pooled_standard_error
import math

def pooled_standard_error(pooled_p, total_a, total_b):
    """Standard error of the difference in two proportions under the pooled null."""
    # TODO: compute sqrt( p*(1-p) * (1/n_a + 1/n_b) ) using the pooled proportion.

    individual_wobble_a = (1-pooled_p)*pooled_p/total_a
    individual_wobble_b = (1-pooled_p)*pooled_p/total_b 

    difference_wobble = individual_wobble_a + individual_wobble_b
    return math.sqrt(difference_wobble)

    pass

# Step 5 - two_proportion_z_statistic
def two_proportion_z_statistic(p_a, p_b, pooled_se):
    # TODO: return the z-statistic for a two-proportion test using p_b - p_a and pooled_se
    return (p_b - p_a)/pooled_se
    pass

# Step 6 - two_sided_p_value
def two_sided_p_value(z):
    # TODO: convert a z-statistic into a two-sided p-value under the standard normal
    one_tail = 1 - standard_normal_cdf((abs(z)))
    return 2*one_tail
    pass

# Step 7 - unpooled_standard_error
def unpooled_standard_error(successes_a, total_a, successes_b, total_b):
    # TODO: return the unpooled SE of the difference between two sample proportions.
    p_A = successes_a/total_a
    p_B = successes_b/total_b 

    var_A = p_A*(1-p_A)/total_a
    var_B = p_B*(1-p_B)/total_b

    SE = math.sqrt(var_A+var_B)
    return SE
    pass

# Step 8 - confidence_interval_from_se
def confidence_interval_from_se(point_estimate, standard_error, confidence_level):
    # TODO: build a two-sided normal-approximation CI (lower, upper) from estimate and SE
    alpha = 1 - confidence_level
    z_star = standard_normal_ppf(1-alpha/2)
    margin = z_star * standard_error
    return (point_estimate-margin, point_estimate+margin)

# Step 9 - required_sample_size_per_variant
import math

def required_sample_size_per_variant(baseline_rate, minimum_detectable_effect, alpha, power):
    #min samples needed per variant for a two-proportion z-test to detect an absolute lift 
    # above baseline rate at a significant level alpha, and "target"???

    p1 = baseline_rate
    p2 = baseline_rate + minimum_detectable_effect

    # Two critical z-values (two-sided test for alpha)
    z_alpha = standard_normal_ppf(1 - alpha / 2)
    z_power = standard_normal_ppf(power)

    # Pooled proportion under the null (equal group sizes, so it's the average)
    p_bar = (p1 + p2) / 2

    null_term = z_alpha * math.sqrt(2 * p_bar * (1 - p_bar))
    alt_term  = z_power * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))

    n = (null_term + alt_term) ** 2 / (p2 - p1) ** 2
    return math.ceil(n)

# Step 10 - statistical_power
import math

def statistical_power(sample_size_per_variant, baseline_rate, effect_size, alpha):
    n = sample_size_per_variant
    p1 = baseline_rate
    p2 = p1 + effect_size

    p_bar = (p1 + p2) / 2
    se_null = math.sqrt(2 * p_bar * (1 - p_bar) / n)
    se_alt  = math.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)

    z_alpha = standard_normal_ppf(1 - alpha / 2)
    threshold = z_alpha * se_null

    z = (abs(effect_size) - threshold) / se_alt
    power = standard_normal_cdf(z)
    return power

# Step 11 - chi_square_statistic
def chi_square_statistic(observed_counts, expected_counts):
    
    #pearson chi-square statistic 
    total = 0.0

    for obs, exp in zip(observed_counts, expected_counts):
        total += (obs-exp)**2/exp
    
    return total

# Step 12 - sample_ratio_mismatch_check
import math
import numpy as np

def sample_ratio_mismatch_check(observed_counts, expected_ratios, alpha):
    # total number of people in the experiment
    total_count = sum(observed_counts)

    expected_counts = [total_count*r for r in expected_ratios]

    chi_square = chi_square_statistic(observed_counts, expected_counts)

    #chi_square = z^2 then z = sqrt(chi_square)

    z = math.sqrt(chi_square)
    p_value = 2* (1-standard_normal_cdf(z))

    srm_detected = p_value < alpha

    return {
    'chi_square': chi_square,
    'p_value': p_value,
    'srm_detected': srm_detected,   
    }

# Step 13 - bonferroni_correction
import numpy as np

def bonferroni_correction(p_values, alpha):
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    if n == 0:
        return np.zeros(0, dtype=bool)      # empty boolean array
    return p < alpha / n

# Step 14 - benjamini_hochberg_correction
import numpy as np

def benjamini_hochberg_correction(p_values, alpha):
    """Return a boolean array marking BH-significant hypotheses at level alpha."""

    p_values_sorted = sorted(enumerate(p_values), key=lambda x: x[1])
    indices = [i for i, p in p_values_sorted]
    rank = [i+1 for i in range(len(p_values))]
    sorted_p = [p for i,p in p_values_sorted]

    

    # n = hypotheses count total
    # alpha*n is the fraction that will lie below that alpha count

    n = len(p_values)
    ans = np.zeros(n, dtype=bool)

    bars = [rank[i]*alpha/n for i in range(len(p_values))]

    k = -1

    for i, p_val in enumerate(sorted_p):
        if p_val <= bars[i]:
            k = i
    
    for i in range(k+1):
        ans[indices[i]] = True

    return ans

# Step 15 - group_mean_change (not yet solved)
# TODO: implement

# Step 16 - difference_in_differences_simple (not yet solved)
# TODO: implement

# Step 17 - build_did_design_matrix (not yet solved)
# TODO: implement

# Step 18 - ols_normal_equations (not yet solved)
# TODO: implement

# Step 19 - did_effect_from_regression (not yet solved)
# TODO: implement

# Step 20 - fit_synthetic_control_weights (not yet solved)
# TODO: implement

# Step 21 - synthetic_control_effect (not yet solved)
# TODO: implement

# Step 22 - ship_decision (not yet solved)
# TODO: implement

