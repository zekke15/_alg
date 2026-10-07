def hanoi_iterative(n, src="A", aux="B", tgt="C"):
    stack = [(n, src, aux, tgt, 0)]
    
    while stack:
        disks, s, a, t, stage = stack.pop()
        if disks == 1:
            print(f"移動盤子 1: {s} -> {t}")
            continue
            
        if stage == 0:
           
            stack.append((disks, s, a, t, 1))
            stack.append((disks - 1, s, t, a, 0))
        else:
            print(f"移動盤子 {disks}: {s} -> {t}")
            stack.append((disks - 1, a, s, t, 0))