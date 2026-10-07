def hanoi_recursive(n, src="A", aux="B", tgt="C"):
    if n == 1:
        print(f"移動盤子 1: {src} -> {tgt}")
        return
    hanoi_recursive(n - 1, src, tgt, aux)
    print(f"移動盤子 {n}: {src} -> {tgt}")
    hanoi_recursive(n - 1, aux, src, tgt)