import argparse
from fractions import Fraction
import json
from math import comb


def multiply(left, right, degree):
    output = [0] * (degree + 1)
    for left_degree, left_value in enumerate(left[:degree + 1]):
        if left_value:
            for right_degree, right_value in enumerate(right[:degree - left_degree + 1]):
                if right_value:
                    output[left_degree + right_degree] += left_value * right_value
    return output


def compose(outer, inner, degree):
    assert inner[0] == 0
    output = [0] * (degree + 1)
    power = [1] + [0] * degree
    for coefficient in outer[:degree + 1]:
        if coefficient:
            output = [value + coefficient * term for value, term in zip(output, power)]
        power = multiply(power, inner, degree)
    return output


def inverse(series, degree):
    assert series[0] == 0 and series[1] == 1
    output = [0, 1] + [0] * (degree - 1)
    powers = [[0] * (degree + 1) for index in range(degree + 1)]
    powers[1][1] = 1
    for current_degree in range(2, degree + 1):
        for exponent in range(2, current_degree + 1):
            powers[exponent][current_degree] = sum(
                output[index] * powers[exponent - 1][current_degree - index]
                for index in range(1, current_degree - exponent + 2)
            )
        output[current_degree] = -sum(
            series[exponent] * powers[exponent][current_degree]
            for exponent in range(2, current_degree + 1)
        )
        powers[1][current_degree] = output[current_degree]
    return output


def integral_family(parameter, cubic, degree):
    assert parameter % 2 == 1 and cubic % 2 == 0
    coefficients = [0, 1] + [0] * (degree - 1)
    square = [0] * (degree + 2)
    square[2] = 1
    for index in range(2, degree + 1):
        target_degree = index + 1
        substitution = (
            parameter ** (target_degree // 2) * coefficients[target_degree // 2]
            if target_degree % 2 == 0 else 0
        )
        cube = sum(coefficients[part] * square[target_degree - part]
                   for part in range(1, index))
        numerator = substitution - square[target_degree] - cubic * cube
        assert numerator % 2 == 0
        coefficients[index] = numerator // 2
        for previous in range(1, index):
            if previous + index <= degree + 1:
                square[previous + index] += 2 * coefficients[previous] * coefficients[index]
        if 2 * index <= degree + 1:
            square[2 * index] += coefficients[index] ** 2
    return coefficients


def rational_coefficients(kind, degree):
    coefficients = [Fraction(0), Fraction(1)]
    for index in range(2, degree + 1):
        target_degree = index + 1
        approximation = coefficients + [Fraction(0)] * (target_degree + 1 - len(coefficients))
        square = multiply(approximation, approximation, target_degree)
        if kind == 'A':
            cube = multiply(square, approximation, target_degree)
            substitution = 3 ** (target_degree // 2) * approximation[target_degree // 2] if target_degree % 2 == 0 else 0
            residual = substitution - square[target_degree] + 2 * cube[target_degree]
        else:
            inner = [2 * value for value in square]
            inner[2] += 1
            inner[3] += 2
            residual = compose(approximation, inner, target_degree)[target_degree] - 3 * square[target_degree]
        coefficients.append(residual / 2)
    return coefficients


def sparse_substitution(series, exponent, scale, degree):
    output = [0] * (degree + 1)
    for index, coefficient in enumerate(series):
        if exponent * index <= degree:
            output[exponent * index] = coefficient * scale ** index
    return output


def check_family_equation(series, parameter, cubic, degree):
    square = multiply(series, series, degree)
    cube = multiply(square, series, degree)
    substitution = sparse_substitution(series, 2, parameter, degree)
    for index in range(degree + 1):
        assert substitution[index] == ((parameter - 1) if index == 2 else 0) + square[index] + cubic * cube[index]


def companion_product(degree, order=2, multiplier=1):
    product = [1] + [0] * degree
    iterate = [0, 1] + [0] * (degree - 1)
    factors = 0
    while any(iterate):
        factor = [multiplier * value for value in iterate]
        factor[0] += 1
        product = multiply(product, factor, degree)
        power = [1] + [0] * degree
        for exponent in range(order):
            power = multiply(power, iterate, degree)
        next_power = multiply(power, iterate, degree)
        iterate = [left + multiplier * right for left, right in zip(power, next_power)]
        factors += 1
    return [0] + product[:degree], factors


def series_power(series, exponent, degree):
    output = [1] + [0] * degree
    for iteration in range(exponent):
        output = multiply(output, series, degree)
    return output


def prime_degree_family(prime, parameter, cubic, degree):
    coefficients = [0, 1] + [0] * (degree - 1)
    for index in range(2, degree + 1):
        target = index + prime - 1
        substituted = sparse_substitution(coefficients, prime, parameter, target)
        power = series_power(coefficients, prime, target)
        higher_power = multiply(power, coefficients, target)
        numerator = substituted[target] - power[target] - cubic * higher_power[target]
        assert numerator % prime == 0
        coefficients[index] = numerator // prime
    target = degree + prime - 1
    substituted = sparse_substitution(coefficients, prime, parameter, target)
    power = series_power(coefficients, prime, target)
    higher_power = multiply(power, coefficients, target)
    power[prime] += parameter - 1
    assert substituted == [left + cubic * right for left, right in zip(power, higher_power)]
    return coefficients


def signed_quadratic(degree):
    coefficients = [0, 1] + [0] * (degree - 1)
    for index in range(2, degree + 1):
        target = index + 1
        substituted = sparse_substitution(coefficients, 2, -1, target)
        square = multiply(coefficients, coefficients, target)
        cube = multiply(square, coefficients, target)
        numerator = -substituted[target] - square[target] + 2 * cube[target]
        assert numerator % 2 == 0
        coefficients[index] = numerator // 2
    substituted = sparse_substitution(coefficients, 2, -1, degree + 1)
    square = multiply(coefficients, coefficients, degree + 1)
    cube = multiply(square, coefficients, degree + 1)
    assert [-value for value in substituted] == [left - 2 * right for left, right in zip(square, cube)]
    return coefficients


def rational_value_bounds(argument, prefix):
    fractional_digits = len(prefix.split('.')[1])
    scale = 10 ** fractional_digits
    expected = Fraction(prefix)
    iterate = argument
    product = Fraction(1)
    for factors in range(1, 17):
        product *= (1 + iterate) ** 2
        iterate = iterate ** 2 + iterate ** 3
        ratio = iterate * (1 + iterate)
        if ratio >= 1:
            continue
        tail = 2 * iterate / (1 - ratio)
        if tail >= 1:
            continue
        lower = argument + argument ** 2 * product
        upper = argument + argument ** 2 * product / (1 - tail)
        if expected <= lower and upper < expected + Fraction(1, scale):
            return {'argument': str(argument), 'decimal_prefix': prefix,
                    'certified_fractional_digits': fractional_digits,
                    'product_factors': factors, 'bound': 'exact rational interval'}
    raise AssertionError('Decimal prefix not certified within sixteen factors')


def run(degree):
    primary = integral_family(3, -2, degree)
    reverse = integral_family(3, 2, degree)
    composition = inverse(reverse, degree)
    square_a = multiply(primary, primary, degree)
    cube_a = multiply(square_a, primary, degree)
    square_b = multiply(composition, composition, degree)
    substituted_a = sparse_substitution(primary, 3, 1, degree)
    check_family_equation(primary, 3, -2, degree + 1)
    check_family_equation(reverse, 3, 2, degree + 1)
    inner = [2 * value for value in square_b]
    inner[2] += 1
    inner[3] += 2
    assert compose(composition, inner, degree) == [3 * value for value in square_b]
    assert compose(reverse, composition, degree) == [0, 1] + [0] * (degree - 1)
    assert compose(composition, reverse, degree) == [0, 1] + [0] * (degree - 1)
    for index in range(degree + 1):
        assert (cube_a[index] - substituted_a[index]) % 3 == 0
        assert (square_a[index] - (1 if index == 2 else 0) - 2 * substituted_a[index]) % 3 == 0
        assert (square_b[index] - (1 if index == 2 else 2 if index == 3 else 0)) % 9 == 0
    checked_exponents = list(range(degree // 3 + 2))
    for series in [primary, composition]:
        power_cube = [1] + [0] * degree
        power_substitution = [1] + [0] * degree
        cube = multiply(multiply(series, series, degree), series, degree)
        substitution = sparse_substitution(series, 3, 1, degree)
        for exponent in checked_exponents:
            assert all((left - right) % 3 == 0 for left, right in zip(power_cube, power_substitution))
            power_cube = multiply(power_cube, cube, degree)
            power_substitution = multiply(power_substitution, substitution, degree)
    assert primary[1:24] == [1, 1, 7, 17, 147, 445, 2199, 9993, 61837, 281417, 1515387, 7844861, 42920817, 232527741, 1297380639, 7159441425, 40375866078, 226515725383, 1286378694156, 7313784351897, 41879211301623, 240239676368409, 1384901325628119]
    assert composition[1:25] == [1, 1, 4, 14, 104, 488, 3291, 18141, 127527, 790427, 5441663, 35375651, 244925743, 1652908531, 11518757017, 79372305657, 557324355555, 3900077626815, 27596212781442, 195214162327620, 1390657027410402, 9919148868199578, 71088535006091553, 510378145935043827]
    rational_degree = 24
    assert rational_coefficients('A', rational_degree) == primary[:rational_degree + 1]
    assert rational_coefficients('B', rational_degree) == composition[:rational_degree + 1]
    inverse_a = inverse(primary, degree)
    inverse_a_square = multiply(inverse_a, inverse_a, degree)
    formula_two_inner = [3 * value for value in inverse_a_square]
    formula_two_right = [2 * value for value in inverse_a_square]
    formula_two_right[2] += 1
    formula_two_right[3] -= 2
    assert compose(primary, formula_two_inner, degree) == formula_two_right
    for index in range(3, degree + 1):
        if index % 2:
            assert square_a[index] == 2 * cube_a[index]
        else:
            assert square_a[index] == 3 ** (index // 2) * primary[index // 2] + 2 * cube_a[index]
    recurrence = [0, 1, 1] + [0] * (degree - 2)
    for index in range(3, degree + 1):
        recurrence[index] = sum(recurrence[part] * comb(part, index + 2 - 2 * part)
                                for part in range((index + 4) // 3, (index + 2) // 2 + 1))
    assert recurrence[1:42] == [1, 1, 2, 3, 6, 9, 14, 24, 42, 72, 114, 179, 284, 453, 736, 1213, 2016, 3362, 5606, 9318, 15378, 25121, 40614, 65216, 104422, 167118, 267674, 429297, 689478, 1109149, 1788032, 2889897, 4683664, 7610640, 12394998, 20225081, 33050490, 54068421, 88519060, 144984819, 237508938]
    for index in range(3, degree + 1):
        if index % 2:
            assert recurrence[index] % 2 == 0
        if index >= 5 and index % 3 == 2:
            assert recurrence[index] % 3 == 0
    linear_inner = [0, 0, 1, 1] + [0] * (degree - 1)
    defining_left = compose(recurrence, linear_inner, degree + 2)
    defining_right = [0, 0, 1] + recurrence[1:]
    assert defining_left == defining_right
    family_examples = []
    for parameter in [-3, 1, 3, 9]:
        for cubic in [-2, 0, 2, 4]:
            example = integral_family(parameter, cubic, 32)
            check_family_equation(example, parameter, cubic, 33)
            family_examples.append([parameter, cubic])
    square_modulus_examples = []
    for parameter in [-3, 1, 3, 5, 9]:
        for cubic in [-2, 0, 2, 4]:
            family = integral_family(parameter, cubic, 32)
            reversed_family = inverse(family, 32)
            reversed_square = multiply(reversed_family, reversed_family, 32)
            substituted_inner = [(parameter - 1) * value for value in reversed_square]
            substituted_inner[2] += 1
            substituted_inner[3] += cubic
            assert compose(reversed_family, substituted_inner, 32) == [
                parameter * value for value in reversed_square]
            difference = list(reversed_square)
            difference[2] -= 1
            difference[3] -= cubic
            assert all(value % (parameter ** 2) == 0 for value in difference)
            assert difference[4] == parameter ** 2 * cubic // 2
            square_modulus_examples.append([parameter, cubic])
    companion, product_factors = companion_product(degree)
    companion_square = multiply(companion, companion, degree)
    linked = list(companion_square)
    linked[1] += 1
    assert linked == recurrence
    assert companion[1:16] == [1, 1, 1, 2, 2, 3, 5, 9, 14, 18, 25, 38, 60, 97, 159]
    assert compose(companion, linear_inner, degree) == [0] + companion[:degree]
    free_second_coefficients = [-2, 0, 1, 3]
    for seed in free_second_coefficients:
        example = [seed * value for value in companion_square]
        example[1] += 1
        left = compose(example, linear_inner, degree)
        right = [0, 0] + example[:degree - 1]
        right[2] += 1
        assert left == right
        assert all(example[index] % 2 == 0 for index in range(3, degree + 1, 2))
        assert all(example[index] % 3 == 0 for index in range(5, degree + 1, 3))
    decimal_checks = [
        rational_value_bounds(Fraction(1, 2), '2.159559553026250611213337771695330430974181015965001'),
        rational_value_bounds(Fraction(2, 5), '0.933573329276106618842623562850786079989669037646701'),
        rational_value_bounds(Fraction(1, 3), '0.607372832553248176009540249167895014820360005807581'),
        rational_value_bounds(Fraction(1, 4), '0.365019912926048482191422544055660211914898834378703'),
        rational_value_bounds(Fraction(1, 5), '0.263568927606249662991971930247996469975567607911732')]
    product_family_examples = []
    for order in [2, 3, 4]:
        for multiplier in [-1, 1]:
            product_series, factors = companion_product(32, order, multiplier)
            reversed_product = inverse(product_series, 32)
            product_inner = [0] * 33
            product_inner[order] = 1
            product_inner[order + 1] = multiplier
            shifted = [0] * (order - 1) + product_series[:34 - order]
            assert compose(product_series, product_inner, 32) == shifted
            assert compose(reversed_product, shifted, 32) == product_inner
            product_family_examples.append([order, multiplier])
    negative_companion, factors = companion_product(32, 2, -1)
    inverse_negative_companion = inverse(negative_companion, 32)
    assert negative_companion[:3] == [0, 1, -1]
    assert inverse_negative_companion[1:12] == [1, 1, 3, 8, 28, 95, 351, 1309, 5056, 19787, 78847]
    cubic_companion, factors = companion_product(32, 3, -1)
    assert cubic_companion[1:12] == [1, -1, 0, -1, 2, -1, 0, 0, 0, -1, 4]
    quartic_companion, factors = companion_product(32, 4, -1)
    inverse_quartic_companion = inverse(quartic_companion, 32)
    assert inverse_quartic_companion[1:12] == [1, 1, 2, 5, 15, 47, 153, 513, 1765, 6193, 22071]
    prime_examples = [[3, 1, -3], [3, 4, 3], [5, 1, -5]]
    prime_series = [prime_degree_family(*parameters, 24) for parameters in prime_examples]
    assert prime_series[0][1:12] == [1, 1, 3, 12, 52, 246, 1224, 6300, 33300, 179643, 985014]
    signed_series = signed_quadratic(32)
    assert signed_series[1:12] == [1, 1, 2, 7, 26, 98, 389, 1617, 6884, 29818, 131284]
    sharpness = {'A389475_cube_degree_4': cube_a[4] - substituted_a[4],
                 'A389475_square_degree_4': square_a[4],
                 'A389474_square_degree_4': square_b[4],
                 'A389472_coefficient_5': recurrence[5]}
    assert list(sharpness.values()) == [3, 15, 9, 6]
    return {'status': 'pass', 'arithmetic': 'exact integers and rational numbers',
            'coefficient_degree': degree, 'A389475_equation_through_degree': degree + 1,
            'A389474_equation_through_degree': degree,
            'A389472_equation_through_degree': degree + 2,
            'source_prefix_lengths': {'A389475': 23, 'A389474': 24, 'A389472': 41,
                                      'A350432': 15, 'A273162': 11, 'A350433': 11,
                                      'A350434': 11, 'A274396': 11, 'A273320': 11},
            'independent_rational_recursion_through_degree': rational_degree,
            'power_exponents': checked_exponents,
            'integral_family_parameter_pairs_through_degree_32': family_examples,
            'square_modulus_parameter_pairs_through_degree_32': square_modulus_examples,
            'companion_product_identity_through_degree': degree,
            'companion_product_factors': product_factors,
            'free_second_coefficients': free_second_coefficients,
            'A389472_rational_value_certificates': decimal_checks,
            'product_family_order_sign_pairs_through_degree_32': product_family_examples,
            'A273162_product_coefficient_2': negative_companion[2],
            'A273162_series_coefficient_2': inverse_negative_companion[2],
            'prime_degree_examples_through_degree_24': prime_examples,
            'signed_quadratic_identity_through_degree': 33,
            'sharpness_coefficients': sharpness,
            'scope': 'Finite coefficient identities; the all-indices proofs are in note.tex.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--degree', type=int, default=96)
    arguments = parser.parse_args()
    if not 41 <= arguments.degree <= 192:
        parser.error('degree must be between 41 and 192')
    print(json.dumps(run(arguments.degree), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
