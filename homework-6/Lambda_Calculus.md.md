## Lambda Calculus 的基本概念

Lambda Calculus（λ 演算）是一種以函數為核心的形式計算系統。純 Lambda Calculus 主要有三種語法：

| 名稱 | Lambda 表達式 | 中文解釋 |
|---|---|---|
| 變數（Variable） | `x` | 代表變數或符號 |
| 函數抽象（Abstraction） | `λx.x` | 定義一個收到 `x` 就回傳 `x` 的函數 |
| 函數應用（Application） | `(λx.x) a` | 把 `a` 傳入前面的函數 |

程式允許使用鍵盤容易輸入的 `\` 代替 `λ`：

```text
λx.x      =  \x.x
λx.λy.x   =  \x.\y.x
```

**有名稱版本是什麼？** 例如 `λx.x`、`λy.y`，變數有 `x`、`y` 這些名稱；解譯器必須正確處理它們的作用範圍。這不是指直接替 Python 函數指定名稱，也不是「函數命名後就能遞迴」。

### 2.1 β 歸約（Beta Reduction）

β 歸約就是把函數的參數代入函數體。

```text
(λx.x) a
→β a
```

這代表原本的 `x` 被參數 `a` 取代。

### 2.2 α 改名（Alpha Conversion）

當參數代換可能使自由變數意外變成綁定變數時，要先更改內部參數名稱。

```text
(λx.λy.x) y
→α (λx.λy_1.x) y
→β λy_1.y
```

如果直接算成 `λy.y`，原本作為參數的自由變數 `y` 就會被錯誤綁定。此處改成新的 `y_1`，是為了避免**變數捕獲**。

### 2.3 正規序（Normal Order）

本程式使用「最左、最外」的策略尋找可化簡的部分，並持續進入 Lambda 函數體內部化簡，直到找不到 β 歸約位置為止，稱為到達**正規形（Normal Form）**。如果表達式不停重複化簡，會在達到設定的步數上限後停止。

## 三、如何執行 Python 解譯器

本專案的主要檔案：

```text
Lambda_Calculus_Interpreter/
├── lambda_calculus.py                 # 解譯器程式
├── test_lambda_calculus.py            # 自動化測試
├── Lambda_Calculus_中文作業說明.md      # 本中文說明文件
├── README.md                          # 專案使用說明
├── AI_開發過程.md                      # AI 協作開發紀錄
├── 執行範例.txt                        # 測試執行輸出
└── run_windows.bat                    # Windows 啟動批次檔
```

1. 安裝 Python 3.10 或更新版本。
2. 在 VS Code 中開啟解壓縮後的專案資料夾。
3. 開啟「終端機 → 新增終端機」。
4. 輸入以下指令：

```powershell
py lambda_calculus.py
```

程式會列出 1～10 組內建範例；輸入編號可以執行範例，輸入 `0` 可以自行輸入新的 Lambda 表達式。

也可以直接指定範例：

```powershell
py lambda_calculus.py --example 2
```

或指定自己的表達式（Windows PowerShell）：

```powershell
py lambda_calculus.py --expr '(\x.x) a'
```

> 注意：在 PowerShell 中，範例可用單引號保護輸入字串。`\` 代表 Lambda；如果顯示 `λ` 有問題，可加上 `--ascii`。若電腦沒有 `py`，可試用 `python`。

## 四、Lambda Calculus 程式輸入：10 組範例

以下範例直接對應 `lambda_calculus.py` 內建的選單編號。表格中 `\` 為 Lambda，不是兩個字元的運算子。

| 編號 | 輸入的 Lambda 程式 | 測試目的 | 最終結果 |
|---|---|---|---|
| 1 | `(\x.x) a` | 恆等函數、基本 β 歸約 | `a` |
| 2 | `((\x.\y.x) a) b` | 連續兩次 β 歸約 | `a` |
| 3 | `(\x.\x.x) a` | 內外層同名變數與遮蔽 | `λx.x` |
| 4 | `(\x.\y.x) y` | α 改名與避免變數捕獲 | `λy_1.y` |
| 5 | `((\x.\y.x) YES) NO` | Church TRUE 選第一個參數 | `YES` |
| 6 | `((\x.\y.y) YES) NO` | Church FALSE 選第二個參數 | `NO` |
| 7 | `(\f.\x.f x) (\z.z)` | 在 Lambda 內部繼續化簡 | `λx.x` |
| 8 | `(\p.p (\a.\b.b) (\a.\b.a)) (\x.\y.x)` | Church NOT TRUE | `λa.λb.b` |
| 9 | `(\x.x x) (\x.x x)` | 無限化簡、步數限制 | **不會得到正規形** |
| 10 | `(\x.\y.x y) y` | α 改名後仍需正確代換 | `λy_1.y y_1` |

**注意：** `YES`、`NO` 在這些例子中只是符號名稱；純 Lambda Calculus 並沒有內建的中文字、Python 布林值或一般算術。

## 五、重要範例的「完整計算過程」與中文說明

以下各步驟是使用本專案的 Python 解譯器執行後得到的結果，並以中文重新整理。`Step 0` 表示起始輸入，因此不計入歸約次數。

### 範例 1：恆等函數

**輸入**：`(\x.x) a`

```text
Step 0 [start] : (λx.x) a
Step 1 [beta]  : a
Result        : a
Status        : NORMAL FORM
```

**中文解釋：** `λx.x` 接收一個參數後就回傳該參數。把 `a` 代入 `x`，得到 `a`。總共 1 次 β 歸約。

### 範例 2：連續代入兩個參數

**輸入**：`((\x.\y.x) a) b`

```text
Step 0 [start] : (λx.λy.x) a b
Step 1 [beta]  : (λy.a) b
Step 2 [beta]  : a
Result        : a
Status        : NORMAL FORM
```

**中文解釋：**

1. 將第一個參數 `a` 代入 `x`，得到 `λy.a`。
2. 再把 `b` 代入內層函數的 `y`。由於函數體 `a` 不使用 `y`，所以結果仍然是 `a`。
3. 共進行 2 次 β 歸約，最後得到 `a`。

### 範例 4：避免變數捕獲（最能展示 α 改名）

**輸入**：`(\x.\y.x) y`

```text
Step 0 [start] : (λx.λy.x) y
Step 1 [alpha] : (λx.λy_1.x) y
Step 2 [beta]  : λy_1.y
Result        : λy_1.y
Alpha steps   : 1
Beta steps    : 1
Total steps   : 2
Status        : NORMAL FORM
```

**中文解釋：**

1. 傳入的參數叫 `y`，而原本的內層函數也叫 `λy`。
2. 如果直接替換，傳入的自由變數 `y` 會被錯誤綁定，所以程式先執行 α 改名，把內層 `y` 改為 `y_1`。
3. 接著把原本函數體中的 `x` 換成參數 `y`，得到 `λy_1.y`。
4. 此範例同時包含 **1 次 α 改名**與 **1 次 β 歸約**。

### 範例 5：Church TRUE

**輸入**：`((\x.\y.x) YES) NO`

```text
Step 0 [start] : (λx.λy.x) YES NO
Step 1 [beta]  : (λy.YES) NO
Step 2 [beta]  : YES
Result        : YES
Status        : NORMAL FORM
```

**中文解釋：** Church TRUE 可以定義成 `λx.λy.x`，因此接收兩個參數後，一律回傳第一個參數 `YES`。

### 範例 6：Church FALSE

**輸入**：`((\x.\y.y) YES) NO`

```text
Step 0 [start] : (λx.λy.y) YES NO
Step 1 [beta]  : (λy.y) NO
Step 2 [beta]  : NO
Result        : NO
Status        : NORMAL FORM
```

**中文解釋：** Church FALSE 定義為 `λx.λy.y`，會選擇第二個參數，因此結果是 `NO`。

### 範例 7：進入函數內部化簡

**輸入**：`(\f.\x.f x) (\z.z)`

```text
Step 0 [start] : (λf.λx.f x) (λz.z)
Step 1 [beta]  : λx.(λz.z) x
Step 2 [beta]  : λx.x
Result        : λx.x
Status        : NORMAL FORM
```

**中文解釋：** 第一次把函數 `λz.z` 傳給 `f`；第二次則在 `λx` 的函數體內，將 `x` 傳給 `λz.z`。由此可看出程式不會只算最外層，而是會繼續化簡到正規形。

### 範例 8：Church NOT TRUE

**輸入**：`(\p.p (\a.\b.b) (\a.\b.a)) (\x.\y.x)`

```text
Step 0 [start] : (λp.p (λa.λb.b) (λa.λb.a)) (λx.λy.x)
Step 1 [beta]  : (λx.λy.x) (λa.λb.b) (λa.λb.a)
Step 2 [beta]  : (λy.λa.λb.b) (λa.λb.a)
Step 3 [beta]  : λa.λb.b
Result        : λa.λb.b
Status        : NORMAL FORM
```

**中文解釋：** NOT 會交換 TRUE 和 FALSE 的選擇結果。此處傳入 TRUE（`λx.λy.x`），最後得到 FALSE（`λa.λb.b`）；變數名稱不同並不影響兩個 Lambda 函數的意義。

### 範例 9：無限化簡與安全限制

**輸入**：`(\x.x x) (\x.x x)`

執行指令（將步數上限設成 3，方便顯示）：

```powershell
py lambda_calculus.py --example 9 --max-steps 3
```

```text
Step 0 [start] : (λx.x x) (λx.x x)
Step 1 [beta]  : (λx.x x) (λx.x x)
Step 2 [beta]  : (λx.x x) (λx.x x)
Step 3 [beta]  : (λx.x x) (λx.x x)
Result        : (λx.x x) (λx.x x)
Status        : STEP LIMIT REACHED (3); not a normal form
```

**中文解釋：** 這個表達式叫做 Ω（Omega），每次 β 化簡後都會回到同一個表達式，不會算出正規形。程式利用最大步數上限避免無限執行；`STEP LIMIT REACHED` **不代表計算成功**。這個例子應用於驗證例外情形的處理。

## 六、程式內部如何運作？

本專案並非直接依靠 Python 的 `lambda` 執行輸入，而是自行寫出解譯器的處理流程：

```text
使用者輸入 Lambda 表達式
            ↓
Tokenize：將符號拆成 Token
            ↓
Parser：建立語法樹 AST
            ↓
尋找最左最外可化簡的位置
            ↓
必要時先做 α 改名（避免變數捕獲）
            ↓
執行 β 歸約（參數代入）
            ↓
列印 Step 編號、步驟類型、運算結果
            ↓
有下一步嗎？── 是 → 繼續化簡
            │
            └── 否 → 輸出正規形與步數統計
```

程式主要由以下函數負責：

| 函數／類別 | 功能 |
|---|---|
| `Var`、`Abs`、`App` | 表達變數、函數抽象與函數應用 |
| `tokenize()`、`parse()` | 分析輸入，建立 AST |
| `free_vars()` | 找出自由變數 |
| `first_required_alpha()` | 檢查是否需要 α 改名 |
| `substitute_safe_after_alpha()` | 在已處理改名後安全代入參數 |
| `find_leftmost_outermost_redex()` | 搜尋下一個可 β 歸約的位置 |
| `reduce_once()` | 一次執行一個 α 或 β 步驟 |
| `normalize()` | 持續歸約，直到完成或達到步數限制 |
| `show_trace()` | 印出完整的計算過程 |

## 七、自動化測試與驗證

在 VS Code 專案資料夾的終端機輸入：

```powershell
py -m unittest -v test_lambda_calculus.py
```

建立專案時，已在 ChatGPT 提供的 Python 執行環境中重新檢查：**22 項測試通過（`Ran 22 tests ... OK`）**。這些測試包括解析語法、β 歸約、α 改名、Church 布林值、在函數體內化簡，以及 Ω 步數限制。

> **誠實註記：** 以上是專案建立環境中的測試結果，不是本人 Windows 電腦的實測。繳交前應在自己電腦重新執行、截圖並填寫下列紀錄。

**本機操作紀錄（自行填寫）：**

- Windows / Python 版本：＿＿＿＿＿＿＿＿
- 執行主程式日期：＿＿＿＿＿＿＿＿
- 執行範例：＿＿＿＿＿＿＿＿
- 是否正確輸出 α、β 步驟：＿＿＿＿＿＿＿＿
- 自動化測試結果：＿＿＿＿＿＿＿＿
- 執行截圖檔名：＿＿＿＿＿＿＿＿

## 八、使用 AI 的網址與開發過程文件

這一節用於回應老師「可用 AI 寫，要分享網址或過程文件」的要求。

### 8.1 Gemini 研究資料

Gemini 分享連結：  
https://gemini.google.com/share/092be7199095

由使用者提供的 Gemini 對話文字整理出以下學習內容：

1. 認識 Lambda Calculus 的變數、函數抽象、函數應用。
2. 學習 α 改名、β 歸約及 η 轉換的用途。
3. 了解 Church TRUE／FALSE、IF、AND、OR、NOT 如何以函數表達。
4. 研究 Church Numerals 與 Y、Z Combinator。
5. 參考 Gemini 提供的 Python `lambda` 範例。

**研究後發現的不足：** Gemini 提供的 Python 範例可以計算布林邏輯、數字及階乘，但沒有將任意輸入的 Lambda 表達式解析成 AST，亦沒有由程式完整印出每一次 α、β 步驟。因此不能直接當作本次解譯器作業繳交。



