# -*- coding: utf-8 -*-
"""第四週第一題：三種固定點迭代公式求 sqrt(3)。"""
import argparse
import math


def calculate(initial=1.0, max_iter=20, tolerance=1e-8):
    if not math.isfinite(initial) or initial == 0:
        raise ValueError('初始值必須是有限且非零的數字')
    if max_iter < 1:
        raise ValueError('迭代次數必須 >= 1')
    x1 = x2 = x3 = float(initial)
    rows = []
    target = math.sqrt(3)
    for i in range(1, max_iter + 1):
        # 即使某方法溢位，其他方法仍可繼續演示
        x1 = 3 / x1 if x1 != 0 and math.isfinite(x1) else float('nan')
        x2 = x2 - (x2*x2 - 3) / 4 if math.isfinite(x2) else float('nan')
        x3 = (x3 + 3 / x3) / 2 if x3 != 0 and math.isfinite(x3) else float('nan')
        rows.append((i, x1, x2, x3, abs(x2-target), abs(x3-target)))
    return rows


def main():
    p = argparse.ArgumentParser(description='三種迭代公式比較：求 sqrt(3)')
    p.add_argument('--initial', type=float, default=1.0, help='初始值，預設 1')
    p.add_argument('--iterations', type=int, default=20, help='迭代次數，預設 20')
    args = p.parse_args()
    print('目標：sqrt(3) = %.10f' % math.sqrt(3))
    print(' 次  | f1: 3/x       | f2: 鬆弛法     | f3: 牛頓法     | f2誤差       | f3誤差')
    print('-' * 94)
    for i,a,b,c,eb,ec in calculate(args.initial,args.iterations):
        print(f'{i:>3}  | {a:>13.9f} | {b:>13.9f} | {c:>13.9f} | {eb:>12.3e} | {ec:>12.3e}')
    print('\n說明：初始值為 1 時，f1 在 1 與 3 之間震盪；f2 緩慢收斂；f3 快速收斂。')

if __name__ == '__main__':
    main()
