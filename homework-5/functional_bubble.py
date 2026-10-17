# -*- coding: utf-8 -*-
"""第五週第三題：自製 map/filter/reduce，禁止所有 for、while 及推導式。"""


def my_map(function, values):
    """遞迴版 map：把 function 套用至所有元素。"""
    result = []

    def visit(index):
        if index == len(values):
            return
        result.append(function(values[index]))
        visit(index + 1)

    visit(0)
    return result


def my_filter(predicate, values):
    """遞迴版 filter：只留下通過條件的元素。"""
    result = []

    def visit(index):
        if index == len(values):
            return
        if predicate(values[index]):
            result.append(values[index])
        visit(index + 1)

    visit(0)
    return result


def my_reduce(function, values, initial):
    """遞迴版 reduce：逐個將元素累積至 initial。"""
    def accumulate(index, total):
        if index == len(values):
            return total
        return accumulate(index + 1, function(total, values[index]))

    return accumulate(0, initial)


def bubble_pass(values):
    """用自製 reduce 完成一輪相鄰比較，把最大值推到最後。"""
    if len(values) < 2:
        return values[:], False

    def compare(state, current):
        output, previous, swapped = state
        if previous > current:
            output.append(current)
            return output, previous, True
        output.append(previous)
        return output, current, swapped

    output, last, swapped = my_reduce(
        compare, values[1:], ([], values[0], False)
    )
    return output + [last], swapped


def bubble_sort(values):
    """使用遞迴取代雙層迴圈，排序結果不會修改原始清單。"""
    data = my_map(lambda value: value, values)  # 自製 map 複製輸入

    def sort_prefix(current, length):
        if length <= 1:
            return current
        arranged, swapped = bubble_pass(current[:length])
        updated = arranged + current[length:]
        if not swapped:  # 一輪都沒交換，表示已經排序完成
            return updated
        return sort_prefix(updated, length - 1)

    return sort_prefix(data, len(data))


def adjacent_pairs(values):
    """遞迴建立相鄰元素的配對，以便檢查排序結果。"""
    if len(values) < 2:
        return []
    return [(values[0], values[1])] + adjacent_pairs(values[1:])


def is_sorted(values):
    """自製 filter：篩選逆序相鄰配對，零組表示已排序。"""
    inversions = my_filter(lambda pair: pair[0] > pair[1], adjacent_pairs(values))
    return len(inversions) == 0


if __name__ == "__main__":
    numbers = [5, 1, 4, 2, 8, 2]
    print("原始清單：", numbers)
    print("my_map（乘二）：", my_map(lambda x: x * 2, numbers))
    print("my_filter（偶數）：", my_filter(lambda x: x % 2 == 0, numbers))
    print("my_reduce（加總）：", my_reduce(lambda total, x: total + x, numbers, 0))
    result = bubble_sort(numbers)
    print("泡沫排序結果：", result)
    print("排序驗證：", is_sorted(result))
    print("原清單未修改：", numbers)
