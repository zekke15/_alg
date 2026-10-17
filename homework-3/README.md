# 第三週習題：列舉法＋暴力搜尋 SAT 問題

## 一、題目要求

> 請寫一個程式可以系統性地列舉真值表，解決 SAT 問題。

參考資料：[Boolean satisfiability problem（維基百科）](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)

本專案使用 **Python 標準函式庫**，透過 `itertools.product` 列舉所有真假組合，對每一組評估布林公式並列出完整真值表，判定公式是 SAT（有解）或 UNSAT（無解）。不需要安裝第三方套件。

## 二、檔案結構

```text
SAT_Truth_Table_Homework/
├── sat_truth_table.py   # 主程式：列舉真值表、判斷 SAT/UNSAT
├── test_sat.py          # 使用 unittest 的自動測試
└── README.md            # 作業解釋、執行方式與演算法分析
```

## 三、SAT 是什麼？

SAT（Boolean Satisfiability Problem，布林可滿足性問題）是判斷**是否存在一組變數的 True/False 設定，使整個布林公式為 True** 的問題。

- **SAT**：至少一組變數設定讓公式成立。
- **UNSAT**：任何變數設定都無法讓公式成立。

### 邏輯運算

| 邏輯符號 | 說明 | Python 寫法 |
|---|---|---|
| `∧` | AND（且） | `and` |
| `∨` | OR（或） | `or` |
| `¬` | NOT（非） | `not` |

## 四、使用的範例公式

本範例：

```text
F = (A OR B) AND (NOT A OR C)
```

程式使用 CNF（Conjunctive Normal Form，合取範式）的列表表示法：**外層列表是 AND；每個內層列表是 OR；`!A` 代表 NOT A**。

```python
formula = [
    ["A", "B"],
    ["!A", "C"],
]
```

這個公式有 A、B、C 三個變數，總共 `2^3 = 8` 種真假組合。

## 五、執行方式（Windows / VS Code）

1. 解壓縮 ZIP，使用 VS Code 開啟 `SAT_Truth_Table_Homework` 資料夾。
2. 開啟 VS Code 的終端機（Terminal → New Terminal）。
3. 確認目前位置在專案資料夾。
4. 在 Windows 執行：

```powershell
py sat_truth_table.py
```

若電腦沒有 `py` 指令，可改用：

```powershell
python sat_truth_table.py
```

macOS / Linux 常見指令：

```bash
python3 sat_truth_table.py
```

**建議使用 Python 3.8 以上版本。**

### 範例輸出

```text
SAT 真值表
A | B | C | F
---------------
0 | 0 | 0 | 0
0 | 0 | 1 | 0
0 | 1 | 0 | 1
0 | 1 | 1 | 1
1 | 0 | 0 | 0
1 | 0 | 1 | 1
1 | 1 | 0 | 0
1 | 1 | 1 | 1

SAT 判斷結果：
SAT：存在滿足條件的解
符合條件的組合數： 4
{'A': False, 'B': True, 'C': False}
{'A': False, 'B': True, 'C': True}
{'A': True, 'B': False, 'C': True}
{'A': True, 'B': True, 'C': True}
```

表格中的 `1` 代表 True，`0` 代表 False。因為有四組讓 F = 1，所以公式屬於 SAT。

## 六、如何驗證 UNSAT？

把 `sat_truth_table.py` 最下方的 `formula` 修改成：

```python
formula = [
    ["A"],
    ["!A"],
]
```

代表 `A AND (NOT A)`。A 不可能同時為真又為假，因此會顯示：

```text
SAT 判斷結果：
UNSAT：不存在滿足條件的解
```

## 七、測試程式

在終端機中執行：

```powershell
py -m unittest -v test_sat.py
```

或者：

```powershell
python -m unittest -v test_sat.py
```

測試包含三變數 SAT、無解公式、簡單 OR、恆真公式、空公式、空子句、四變數及輸入格式驗證。

## 八、演算法分析

程式核心流程：

1. 從公式取得所有變數。
2. 使用 `itertools.product((False, True), repeat=n)` 產生所有 `2^n` 種組合。
3. 將每一組設定代入公式，逐一檢查每個 OR 子句；所有子句都成立才得到 True。
4. 列印真值表，並保存所有使公式成立的組合。
5. 有至少一組成立則輸出 SAT，否則輸出 UNSAT。

令 `n` 為不同變數的數量、`L` 為公式中文字項（literal）總數。

- 全部真假組合數量：`2^n`。
- 一組設定最壞需檢查 `L` 個文字項，因此時間複雜度約為 **O(2^n × (n + L))**（包含建立每組變數字典及輸出資料列；若僅考慮公式評估則為 O(2^n × L)）。
- 本程式會保存全部真值表，因此空間複雜度至少為 **O(2^n × n)**；不包含輸出字串。

暴力法優點是容易理解、可完整列出所有可能；缺點是變數增加時執行量呈指數成長，不適合大型 SAT 題目。

## 九、作業繳交建議

1. 保留 `sat_truth_table.py`、`test_sat.py`、`README.md`。
2. 自己在電腦上執行主程式，截取 SAT 真值表畫面。
3. 修改成 UNSAT 公式並再次執行，截取 UNSAT 輸出。
4. 執行自動測試並截圖，必要時附在作業系統中。
5. 若老師要求個人心得，可依實際操作情形補上觀察，不要把預期輸出描述為個人實測結果。
