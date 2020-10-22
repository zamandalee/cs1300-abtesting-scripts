# WALKTHROUGH: https://cs1300-abtesting.herokuapp.com/

from scipy import stats
from scipy.stats import t as t_dist
from scipy.stats import chi2

from abtesting_test import *

# print(t_dist.cdf(-2, 20)) # should print .02963
# print(t_dist.cdf(2, 20)) # positive t-score (bad), should print .97036 (= 1 - .2963)
# print(chi2.cdf(23.6, 12)) # prints 0.976
# print(1 - chi2.cdf(23.6, 12)) # prints 1 - 0.976 = 0.023 (yay!)

# T-SCORE:
def slice_2D(list_2D, start_row, end_row, start_col, end_col):
    '''
    Splices a the 2D list via start_row:end_row and start_col:end_col
    :param list: list of list of numbers
    :param nums: start_row, end_row, start_col, end_col
    :return: the spliced 2D list (ending indices are exclsive)
    '''
    to_append = []
    for l in range(start_row, end_row):
        to_append.append(list_2D[l][start_col:end_col])

    return to_append

def get_avg(nums):
    '''
    Helper function for calculating the average of a sample.
    :param nums: list of numbers
    :return: average of list
    '''
    return sum(nums) / len(nums)

def get_stdev(nums):
    '''
    Helper function for calculating the standard deviation of a sample.
    :param nums: list of numbers
    :return: standard deviation of list
    '''
    avg = get_avg(nums)
    summation = 0
    for n in nums:
        summation += (n - avg) ** 2

    return (summation / (len(nums) - 1)) ** 0.5

def get_se(a, b):
    '''
    Helper function for calculating the standard error, given two samples.
    :param a: list of numbers
    :param b: list of numbers
    :return: standard error of a and b (see studio 6 guide for this equation!)
    '''
    std_a, std_b = get_stdev(a), get_stdev(b)
    n_a, n_b = len(a), len(b)
    return (
        (std_a ** 2 / n_a) + (std_b ** 2 / n_b)
    ) ** 0.5

def get_2_sample_df(a, b):
    '''
    Calculates the combined degrees of freedom between two samples.
    :param a: list of numbers
    :param b: list of numbers
    :return: integer representing the degrees of freedom between a and b (see studio 6 guide for this equation!)
    '''
    std_a, std_b = get_stdev(a), get_stdev(b)
    n_a, n_b = len(a), len(b)

    se_4 = get_se(a, b) ** 4
    denom_a = (std_a ** 2 / n_a) ** 2 / (n_a - 1)
    denom_b = (std_b ** 2 / n_b) ** 2 / (n_b - 1)

    return round(
        se_4 / (denom_a + denom_b)
    )

def get_t_score(a, b):
    '''
    Calculates the t-score, given two samples.
    :param a: list of numbers
    :param b: list of numbers
    :return: number representing the t-score given lists a and b (see studio 6 guide for this equation!)
    '''
    t_score = (get_avg(a) - get_avg(b)) / get_se(a, b)
    if t_score > 0:
        return -1 * t_score
    return t_score

def perform_2_sample_t_test(a, b):
    '''
    ** DO NOT CHANGE THE NAME OF THIS FUNCTION!! **
    Calculates a p-value by performing a 2-sample t-test, given two lists of numbers.
    :param a: list of numbers
    :param b: list of numbers
    :return: calculated p-value
    '''
    return t_dist.cdf(get_t_score(a, b), get_2_sample_df(a, b))



# CHI^2:
def row_sum(observed_grid, el_row):
    return sum(observed_grid[el_row])
def col_sum(observed_grid, el_col):
    total = 0
    for row in observed_grid:
        total += row[el_col]
    return total
def total_sum(observed_grid):
    total = 0
    for row in observed_grid:
        total += sum(row)
    return total
def calculate_expected(row_sum, col_sum, total_sum):
    return row_sum * col_sum / total_sum

def get_expected_grid(observed_grid):
    '''
    Calculates the expected counts, given the observed counts.
    :param observed_grid: 2D list of observed counts
    :return: 2D list of expected counts
    '''
    expected_grid = []
    tot_sum = total_sum(observed_grid)

    for i in range(0, len(observed_grid)):
        curr_row = observed_grid[i]
        expected_row = []
        for j in range (0, len(curr_row)):
            i_sum = row_sum(observed_grid, i)
            j_sum = col_sum(observed_grid, j)
            expected_row.append(calculate_expected(i_sum, j_sum, tot_sum))
        expected_grid.append(expected_row)

    return expected_grid

def df_chi2(observed_grid):
    '''
    Calculates the degrees of freedom of the expected counts.
    :param observed_grid: 2D list of observed counts
    :return: degrees of freedom of expected counts (see studio 6 guide for this equation!)
    '''
    return (len(observed_grid) - 1) * (len(observed_grid[0]) - 1)

def chi2_value(observed_grid):
    '''
    Calculates the chi^2 value of the expected counts.
    :param observed_grid: 2D list of observed counts
    :return: associated chi^2 value of expected counts (see studio 6 guide for this equation!)
    '''
    # Populate chi^2 grid
    expected_grid = get_expected_grid(observed_grid)
    chi2_grid = []
    for i in range(0, len(observed_grid)):
        curr_row = observed_grid[i]
        chi2_row = []
        for j in range (0, len(curr_row)):
            observed = observed_grid[i][j]
            expected = expected_grid[i][j]
            chi2_val = (observed - expected) ** 2 / expected
            chi2_row.append(chi2_val)
        chi2_grid.append(chi2_row)

    return total_sum(chi2_grid) # QUESTION summation? what?

def perform_chi2_homogeneity_test(observed_grid):
    '''
    ** DO NOT CHANGE THE NAME OF THIS FUNCTION!! **
    Calculates the p-value by performing a chi^2 test, given a list of observed counts
    :param observed_grid: 2D list of observed counts
    :return: calculated p-value
    '''
    chi2_val = chi2_value(observed_grid)
    if chi2_val > 0:
        return 1 - chi2.cdf(chi2_val, df_chi2(observed_grid))
    else:
        return chi2.cdf(chi2_val, df_chi2(observed_grid))

def data_to_num_list(s):
  '''
    Takes a copy and pasted row/col from a spreadsheet and produces a usable list of nums.
    This will be useful when you need to run your tests on your cleaned log data!
    :param str: string holding data
    :return: the spliced list of numbers
    '''
  return list(map(float, s.split()))


# TESTS
# t_test 1:
a_t1_list = data_to_num_list(a1)
b_t1_list = data_to_num_list(b1)
print(get_t_score(a_t1_list, b_t1_list)) # this should be -129.500
print(perform_2_sample_t_test(a_t1_list, b_t1_list)) # this should be 0.0000

# t_test 2:
a_t2_list = data_to_num_list(a2)
b_t2_list = data_to_num_list(b2)
print(get_t_score(a_t2_list, b_t2_list)) # this should be -1.48834
print(perform_2_sample_t_test(a_t2_list, b_t2_list)) # this should be .082379

# t_test 3:
a_t3_list = data_to_num_list(a3)
b_t3_list = data_to_num_list(b3)
print(get_t_score(a_t3_list, b_t3_list)) # this should be -2.88969
print(perform_2_sample_t_test(a_t3_list, b_t3_list)) # this should be .005091

# chi2_test 1:
a_c1_list = data_to_num_list(a_count_1)
b_c1_list = data_to_num_list(b_count_1)
c1_observed_grid = [a_c1_list, b_c1_list]
print("\n\nCHI2 TEST 1: ", chi2_value(c1_observed_grid)) # this should be 4.103536
print(perform_chi2_homogeneity_test(c1_observed_grid)) # this should be .0427939

# chi2_test 2:
a_c2_list = data_to_num_list(a_count_2)
b_c2_list = data_to_num_list(b_count_2)
c2_observed_grid = [a_c2_list, b_c2_list]
print("\nCHI2 TEST 2: ", chi2_value(c2_observed_grid)) # this should be 33.86444
print(perform_chi2_homogeneity_test(c2_observed_grid)) # this should be 0.0000

# chi2_test 3:
a_c3_list = data_to_num_list(a_count_3)
b_c3_list = data_to_num_list(b_count_3)
c3_observed_grid = [a_c3_list, b_c3_list]
print("\nCHI2 TEST 3: ", chi2_value(c3_observed_grid)) # this should be .3119402
print(perform_chi2_homogeneity_test(c3_observed_grid)) # this should be .57649202


