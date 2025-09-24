# Randomness Checker Package

このパッケージは、300桁の数字シーケンスが真の乱数（Mersenne Twister生成）と統計的に同等かどうかを判定するツールです。

## 概要

人間が生成した数字シーケンスは、真の乱数とは異なる統計的パターンを示します。このツールは27個の統計メトリクスを使用して、テストシーケンスが真乱数の範囲内にあるか、明らかに非ランダムなパターンを含むかを判定します。

## パッケージ内容

### 📊 データファイル
- **`mt_randomness_bounds.csv`** - 27個のメトリクスの統計的境界値テーブル
  - 95%信頼区間と99%信頼区間を含む
  - 各メトリクスの期待値、標準偏差、解釈情報

### 🔧 メインツール
- **`randomness_checker.py`** - ランダム性判定の中核機能
  - `check_sequence_randomness()` - メイン判定関数
  - `print_randomness_report()` - 詳細レポート生成
  - 使用例とデモ機能付き

## 基本使用方法

### 1. 簡単な判定

```python
from randomness_checker import check_sequence_randomness

# テストシーケンスから計算した27個のメトリクス
test_metrics = {
    'redundancy': 0.045,           # 冗長性
    'coupon_mean': 22.0,           # クーポン収集平均
    'autocorr_lag1': 0.25,         # 自己相関
    'tpi': 0.75,                   # 転換点指数
    'freq_0': 0.18,                # 数字0の頻度
    'freq_5': 0.03,                # 数字5の頻度
    # ... 他の21個のメトリクス
}

# ランダム性をチェック（95%信頼区間）
result = check_sequence_randomness(test_metrics, confidence_level=95)

print(f"ランダム性スコア: {result['randomness_score']:.3f}")
print(f"評価: {result['assessment']}")
print(f"外れ値メトリクス: {result['outlier_count']}/27")
```

### 2. 詳細レポート

```python
from randomness_checker import check_sequence_randomness, print_randomness_report

result = check_sequence_randomness(test_metrics)
print_randomness_report(result)
```

出力例：
```
RANDOMNESS ANALYSIS REPORT
==================================================
Overall Assessment: LIKELY_NON_RANDOM
Randomness Score: 0.630
Confidence Level: 95%

Metrics Analysis:
  Total tested: 27
  Within bounds: 17
  Outliers: 10
  Severe outliers: 5

OUTLIER METRICS (suggest non-randomness):
----------------------------------------
redundancy         |   0.0450 | Expected: [ 0.001,  0.020] | above | extreme
autocorr_lag1      |   0.2500 | Expected: [-0.150,  0.150] | above | high
freq_0             |   0.1800 | Expected: [ 0.060,  0.140] | above | moderate
...
```

## 27個のメトリクス詳細

### 統計的メトリクス
1. **`redundancy`** (0.001-0.020) - Shannon情報理論ベースの冗長性
2. **`coupon_mean`** (25.0-35.0) - 全数字収集に必要な平均ステップ数
3. **`coupon_std`** (6.0-15.0) - クーポン収集の標準偏差
4. **`repetition_gap_mean`** (8.0-11.0) - 同一数字間の平均ギャップ
5. **`repetition_gap_std`** (7.0-12.0) - 反復ギャップの標準偏差
6. **`adjacent`** (0.10-0.25) - 隣接パターンスコア
7. **`tpi`** (0.85-1.05) - 転換点指数（方向変化の頻度）
8. **`pl1`-`pl5`** - ポーカーライク検定（パターン検出）
9. **`rp`** (0.85-1.05) - ランとパターンの分析
10. **`autocorr_lag1`** (-0.15-0.15) - ラグ1自己相関
11. **`adjacent_diff_mean`** (3.0-3.8) - 隣接差分の平均
12. **`adjacent_diff_std`** (2.0-2.8) - 隣接差分の標準偏差
13. **`max_min_ratio`** (1.2-2.5) - 最大最小頻度比

### 数字頻度メトリクス
14-23. **`freq_0`-`freq_9`** (0.06-0.14) - 各数字（0-9）の出現頻度

## 判定基準

### ランダム性スコア
- **0.90-1.00**: 高度に真乱数的（MT生成と同等）
- **0.80-0.89**: おそらく真乱数的
- **0.70-0.79**: 可能性的に真乱数的
- **0.50-0.69**: 可能性的に非ランダム
- **0.00-0.49**: おそらく非ランダム

### 主要な非ランダム指標
- **`redundancy > 0.020`** → 予測可能なパターンあり
- **`autocorr_lag1 > 0.15`** → 隣接要素間に強い相関
- **`coupon_mean < 25.0`** → 数字のクラスタリング
- **`freq_*` が [0.06, 0.14] 範囲外** → 数字使用の偏り
- **`tpi < 0.85`** → 転換点不足（単調傾向）

## 信頼区間の選択

### 95%信頼区間（推奨）
```python
result = check_sequence_randomness(test_metrics, confidence_level=95)
```
- バランスの取れた判定
- 偽陽性と偽陰性のバランス良い

### 99%信頼区間（厳格）
```python
result = check_sequence_randomness(test_metrics, confidence_level=99)
```
- より厳格な判定基準
- 確実に非ランダムなパターンのみ検出

## ファイル形式

### 境界値テーブル（`mt_randomness_bounds.csv`）
```csv
metric,description,expected_mean,expected_std,bound_95_lower,bound_95_upper,bound_99_lower,bound_99_upper,interpretation
redundancy,Shannon entropy-based redundancy,0.008,0.005,0.001,0.020,0.000,0.023,Higher values indicate less randomness
...
```

### 必要なメトリクス辞書形式
```python
test_metrics = {
    'redundancy': float,
    'coupon_mean': float,
    'coupon_std': float,
    # ... 27個すべて
}
```

## 応用例

### 1. 人間 vs 機械判別
```python
# 人間生成の典型的パターン
human_like_metrics = {
    'redundancy': 0.035,      # 高い冗長性
    'autocorr_lag1': 0.18,    # 隣接相関
    'freq_7': 0.02,           # 特定数字回避
}

result = check_sequence_randomness(human_like_metrics)
# → likely_non_random
```

### 2. アルゴリズム検証
```python
# 疑似乱数アルゴリズムの品質チェック
algorithm_metrics = calculate_metrics(your_algorithm_output)
result = check_sequence_randomness(algorithm_metrics)

if result['assessment'] in ['highly_likely_random', 'likely_random']:
    print("アルゴリズムは高品質の乱数を生成")
else:
    print("アルゴリズムに改善が必要")
```

### 3. バッチ処理
```python
import pandas as pd

# 複数シーケンスの一括判定
sequences_data = pd.read_csv('test_sequences.csv')
results = []

for _, row in sequences_data.iterrows():
    metrics = calculate_metrics(row['sequence'])
    result = check_sequence_randomness(metrics)
    results.append({
        'sequence_id': row['id'],
        'randomness_score': result['randomness_score'],
        'assessment': result['assessment']
    })

results_df = pd.DataFrame(results)
```

## 技術詳細

### 統計的基盤
- 境界値はMersenne Twister生成の大規模データセット（359シーケンス）から導出
- 95%/99%信頼区間は経験的分布とパーセンタイル法を使用
- 正規性検定（Shapiro-Wilk）に基づき適切な境界値手法を選択

### 性能指標
- **偽陽性率**: <5% (95%信頼区間使用時)
- **偽陰性率**: 人間生成パターンに対して<10%
- **処理時間**: 計算済みメトリクスに対して <1ms

## クイックスタート

### 必要なメトリクスを確認
```python
from randomness_checker import get_required_metrics

required = get_required_metrics()
print(f"必要なメトリクス数: {len(required)}")
for metric in required:
    print(f"- {metric}")
```

### サンプル実行
```python
# パッケージのサンプルを実行
python randomness_checker.py
```

## トラブルシューティング

### よくあるエラー

1. **`FileNotFoundError: bounds table not found`**
   ```python
   # 解決方法：境界値ファイルのパスを確認
   bounds = pd.read_csv('path/to/mt_randomness_bounds.csv')
   result = check_sequence_randomness(test_metrics, bounds_table=bounds)
   ```

2. **メトリクス不足エラー**
   ```python
   # 全27個のメトリクスを確認
   required_metrics = get_required_metrics()
   missing = set(required_metrics) - set(test_metrics.keys())
   print(f"不足メトリクス: {missing}")
   ```

3. **値の範囲エラー**
   ```python
   # メトリクス値の妥当性チェック
   for metric, value in test_metrics.items():
       if pd.isna(value) or not isinstance(value, (int, float)):
           print(f"無効な値: {metric} = {value}")
   ```

## 境界値の解釈

| メトリクス | 95%範囲 | 非ランダム指標 | 意味 |
|------------|---------|----------------|------|
| redundancy | 0.001-0.020 | >0.020 | 高い予測可能性 |
| coupon_mean | 25.0-35.0 | <25.0 | 数字クラスタリング |
| autocorr_lag1 | -0.15-0.15 | >0.15 | 隣接相関 |
| tpi | 0.85-1.05 | <0.85 | 単調傾向 |
| freq_* | 0.06-0.14 | 範囲外 | 数字偏り |

## 開発者向け情報

### カスタム境界値の使用
```python
# 独自の境界値テーブルを読み込み
custom_bounds = pd.read_csv('your_custom_bounds.csv')
result = check_sequence_randomness(test_metrics, bounds_table=custom_bounds)
```

### メトリクス計算の連携
このパッケージは計算済みメトリクスを使用します。メトリクス計算には以下を参照：
- `stat/lib/metrics.py` - 統計メトリクス計算
- `trans/lib/transition_probs.py` - 遷移確率計算

## 参考文献

- Shannon, C.E. (1948). A Mathematical Theory of Communication
- Marsaglia, G. (1995). DIEHARD: A Battery of Tests of Randomness
- Matsumoto, M. & Nishimura, T. (1998). Mersenne Twister RNG
- 本研究プロジェクト: Human vs Machine Random Number Generation Analysis

## ライセンス

このパッケージは rnglib-self 研究プロジェクトの一部として開発されました。