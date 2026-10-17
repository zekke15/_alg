# -*- coding: utf-8 -*-
"""第五週第一題：河內塔（遞迴版與非遞迴版）。"""


def _validate(n, source, auxiliary, target):
    if type(n) is not int or n < 0:
        raise ValueError("n 必須是非負整數")
    if len({source, auxiliary, target}) != 3:
        raise ValueError("三根柱子名稱不可相同")


def hanoi_recursive(n, source="A", auxiliary="B", target="C"):
    """用函式遞迴，回傳 (圓盤編號, 起點, 終點) 的移動清單。"""
    _validate(n, source, auxiliary, target)
    moves = []

    def solve(k, start, spare, end):
        if k == 0:
            return
        solve(k - 1, start, end, spare)
        moves.append((k, start, end))
        solve(k - 1, spare, start, end)

    solve(n, source, auxiliary, target)
    return moves


def hanoi_iterative(n, source="A", auxiliary="B", target="C"):
    """不用遞迴，改用堆疊模擬待執行的指令。"""
    _validate(n, source, auxiliary, target)
    moves = []
    stack = [("solve", n, source, auxiliary, target)]

    while stack:
        action, k, start, spare, end = stack.pop()
        if action == "move":
            moves.append((k, start, end))
        elif k > 0:
            # 堆疊後進先出：先放第二階段，再放移動，再放第一階段。
            stack.append(("solve", k - 1, spare, start, end))
            stack.append(("move", k, start, spare, end))
            stack.append(("solve", k - 1, start, end, spare))

    return moves


def show_moves(title, moves):
    print(title)
    for step, (disk, start, end) in enumerate(moves, start=1):
        print(f"第 {step} 步：圓盤 {disk} 從 {start} 移到 {end}")
    print(f"共 {len(moves)} 步\n")


if __name__ == "__main__":
    n = 3
    recursive_moves = hanoi_recursive(n)
    iterative_moves = hanoi_iterative(n)
    show_moves("【遞迴版】", recursive_moves)
    show_moves("【非遞迴版】", iterative_moves)
    print("兩種方法結果相同：", recursive_moves == iterative_moves)
    print("符合最少步數 2^n - 1：", len(recursive_moves) == 2**n - 1)
