def bubble_pass(acc, item):
    """
    acc 格式: (current_bubble, sorted_sublist)
    若 item < current_bubble，則將 item 放進已排序串列，保留 current_bubble 繼續往下推。
    """
    bubble, processed = acc
    if bubble <= item:
        return (item, processed + [bubble])
    else:
        return (bubble, processed + [item])

def single_bubble_run(lst):
    if len(lst) <= 1:
        return lst

    last_bubble, remainder = my_reduce(bubble_pass, lst[1:], (lst[0], []))
    return remainder + [last_bubble]

def bubble_sort_no_loops(lst):
    if len(lst) <= 1:
        return lst

    steps = my_map(lambda x: None, lst)
    
    return my_reduce(lambda current_list, _: single_bubble_run(current_list), steps, lst)


test_data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = bubble_sort_no_loops(test_data)
print("排序結果:", sorted_data)
