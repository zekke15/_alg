# -*- coding: utf-8 -*-
"""比較四種計算 2^n 的方法；避免對指數級遞迴測試 n=100。"""
from functools import lru_cache
from time import perf_counter


def power2n_direct(n):
    return 2 ** n


def power2n_double_recursive(n):
    if n == 0:
        return 1
    return power2n_double_recursive(n - 1) + power2n_double_recursive(n - 1)


def power2n_single_recursive(n):
    if n == 0:
        return 1
    return 2 * power2n_single_recursive(n - 1)


def power2n_memo(n):
    cache = {0: 1}

    def solve(k):
        if k not in cache:
            cache[k] = solve(k - 1) + solve(k - 1)
        return cache[k]

    return solve(n)


def benchmark(func, n, repeats=5):
    measurements = []
    value = None
    for _ in range(repeats):
        start = perf_counter()
        value = func(n)
        measurements.append(perf_counter() - start)
    return value, min(measurements) * 1000


def main():
    n = 100
    methods = [
        ('方法1：直接次方', power2n_direct),
        ('方法2a：雙重遞迴', power2n_double_recursive),
        ('方法2b：單次遞迴', power2n_single_recursive),
        ('方法3：遞迴 + 查表', power2n_memo),
    ]
    expected = 2 ** n
    print(f'測試 n = {n}')
    print(f'正確答案：{expected}\n')
    for name, func in methods:
        if func is power2n_double_recursive:
            small_n = 20
            value, elapsed = benchmark(func, small_n, repeats=1)
            assert value == 2 ** small_n
            print(f'{name}：n=100 跳過（時間 O(2^n)，無法合理完成）')
            print(f'  改測 n={small_n}：結果={value}，耗時={elapsed:.4f} ms')
        else:
            value, elapsed = benchmark(func, n)
            assert value == expected
            print(f'{name}：結果正確，最快單次耗時={elapsed:.4f} ms')


if __name__ == '__main__':
    main()
