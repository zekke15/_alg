# -*- coding: utf-8 -*-
"""遞迴關係式四題：精確值、公式與 Big O。Python 3，無需外部套件。"""


def t1(n):
    if n < 1:
        raise ValueError('n 必須 >= 1')
    if n == 1:
        return 1
    return t1(n - 1) + 8


def t2(n):
    if n < 1:
        raise ValueError('n 必須 >= 1')
    if n == 1:
        return 1
    return 2 * t2(n - 1) + 9


def check_power_of_two(n):
    if n < 1 or n & (n - 1):
        raise ValueError('第 3、4 題要求 n 是正整數且為 2 的次方')


def t3(n):
    check_power_of_two(n)
    if n == 1:
        return 1
    return 2 * t3(n // 2) + 1


def t4(n):
    check_power_of_two(n)
    if n == 1:
        return 1
    return t4(n // 2) + 1


def formulas(n):
    check_power_of_two(n)
    return 8 * n - 7, 10 * 2 ** (n - 1) - 9, 2 * n - 1, n.bit_length()


def main():
    print('四題遞迴關係式：遞迴計算與精確公式驗證')
    print('  n |      T1 |         T2 |      T3 |      T4 | 驗證')
    print('-' * 65)
    for n in [1, 2, 4, 8, 16]:
        values = (t1(n), t2(n), t3(n), t4(n))
        expected = formulas(n)
        print(f'{n:3} | {values[0]:7} | {values[1]:10} | {values[2]:7} | {values[3]:7} | {"通過" if values == expected else "失敗"}')
    print('\n精確公式與 Big O：')
    print('1. T(n) = 8n - 7;               O(n)')
    print('2. T(n) = 10 * 2^(n-1) - 9;    O(2^n)')
    print('3. T(n) = 2n - 1;              O(n)')
    print('4. T(n) = log2(n) + 1;         O(log n)')
    print('註：第 3、4 題採 n 為 2 的正整數次方。')


if __name__ == '__main__':
    main()
