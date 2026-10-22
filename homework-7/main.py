# -*- coding: utf-8 -*-
"""簡易 grep：動態規劃（DP）與 Thompson NFA 比較。只支援字面字元、.、*。"""
import argparse
import time
from pathlib import Path


def validate_pattern(pattern):
    """* 只能接在字元或 . 後方，也不允許連續 *。"""
    for i, ch in enumerate(pattern):
        if ch == '*' and (i == 0 or pattern[i - 1] == '*'):
            raise ValueError("不合法的正規表達式：* 必須接在字元或 . 之後，且不可連續使用")


def dp_search(text, pattern):
    """判斷文字中是否存在符合 pattern 的子字串；O(nm) 時間與空間。"""
    validate_pattern(pattern)
    n, m = len(text), len(pattern)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = True  # 可從文字任意位置開始匹配
    for j in range(2, m + 1):
        if pattern[j - 1] == '*':
            dp[0][j] = dp[0][j - 2]
    if dp[0][m]:
        return True
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            p = pattern[j - 1]
            if p == '*':
                dp[i][j] = dp[i][j - 2] or (
                    (pattern[j - 2] == '.' or pattern[j - 2] == text[i - 1])
                    and dp[i - 1][j]
                )
            elif p == '.' or p == text[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
        if dp[i][m]:
            return True
    return False


def compile_nfa(pattern):
    """Thompson 型 NFA：回傳 transitions, eps, start, accept。"""
    validate_pattern(pattern)
    transitions, eps = [], []

    def state():
        transitions.append([])
        eps.append([])
        return len(transitions) - 1

    start = state()
    current = start
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        repeat = i + 1 < len(pattern) and pattern[i + 1] == '*'
        if repeat:
            entry = state()
            loop_start = state()
            exit_state = state()
            eps[current].append(entry)
            eps[entry].extend([loop_start, exit_state])
            transitions[loop_start].append((ch, loop_start))
            eps[loop_start].append(exit_state)
            current = exit_state
            i += 2
        else:
            nxt = state()
            transitions[current].append((ch, nxt))
            current = nxt
            i += 1
    return transitions, eps, start, current


def epsilon_closure(states, eps):
    seen = set(states)
    stack = list(states)
    while stack:
        s = stack.pop()
        for nxt in eps[s]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def nfa_search(text, pattern):
    """模擬 NFA 同時追蹤所有可能狀態；O(nm) 時間、O(m) 額外空間。"""
    transitions, eps, start, accept = compile_nfa(pattern)
    initial = epsilon_closure({start}, eps)
    active = initial
    if accept in active:
        return True
    for char in text:
        # 每個字元都允許重新開始，模擬 grep 子字串搜尋
        active |= initial
        following = set()
        for s in active:
            for label, dest in transitions[s]:
                if label == '.' or label == char:
                    following.add(dest)
        active = epsilon_closure(following, eps)
        if accept in active:
            return True
    return False


def grep_lines(lines, pattern, search_fn):
    return [(i, line.rstrip('\r\n')) for i, line in enumerate(lines, 1)
            if search_fn(line.rstrip('\r\n'), pattern)]


def benchmark(text, pattern, repeats=20):
    """每次重複測試同樣輸入，報告每次搜尋平均耗時。"""
    if repeats < 1:
        raise ValueError('repeats 必須大於零')
    results = {}
    for name, fn in [('DP', dp_search), ('NFA', nfa_search)]:
        start = time.perf_counter()
        for _ in range(repeats):
            result = fn(text, pattern)
        elapsed = time.perf_counter() - start
        results[name] = (result, elapsed / repeats * 1000)
    return results


def main():
    parser = argparse.ArgumentParser(description='簡易 grep：DP vs NFA')
    parser.add_argument('pattern', nargs='?', default='c.t', help='簡易正規表達式')
    parser.add_argument('file', nargs='?', help='UTF-8 文字檔案（未指定時使用內建例子）')
    parser.add_argument('--benchmark', action='store_true', help='進行效能測試')
    parser.add_argument('--repeats', type=int, default=20, help='測試重複次數')
    args = parser.parse_args()
    try:
        validate_pattern(args.pattern)
        if args.file:
            lines = Path(args.file).read_text(encoding='utf-8-sig').splitlines()
        else:
            lines = ['hello world', 'hello Python', 'cat', 'cut', 'cot', 'dog', 'abbc', 'ac']
        print(f'搜尋模式：{args.pattern!r}')
        for name, fn in [('DP', dp_search), ('NFA', nfa_search)]:
            matches = grep_lines(lines, args.pattern, fn)
            print(f'\n{name} 匹配結果（{len(matches)} 行）：')
            for no, line in matches:
                print(f'第 {no} 行：{line}')
        if args.benchmark:
            text = '\n'.join(lines)
            print(f'\n效能測試：字元數={len(text)}，重複={args.repeats} 次')
            for name, (matched, milliseconds) in benchmark(text, args.pattern, args.repeats).items():
                print(f'{name}：匹配={matched}，平均 {milliseconds:.6f} ms')
    except (ValueError, OSError, UnicodeError) as e:
        parser.error(str(e))


if __name__ == '__main__':
    main()
