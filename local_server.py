#!/usr/bin/env python3
"""
ローカルサーバー - Python分類機を直接使用するWebアプリ
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import sys
import os
sys.path.append('./exported_classifier')
sys.path.append('./checker')

from calculate_features import calculate_all_features
from randomness_checker import check_sequence_randomness, print_randomness_report
import pickle
import pandas as pd

app = Flask(__name__)

# 分類機を起動時に読み込み
classifier_data = None
model = None
scaler = None

def load_classifier():
    global classifier_data, model, scaler
    try:
        with open('./exported_classifier/human_machine_classifier.pkl', 'rb') as f:
            classifier_data = pickle.load(f)
        model = classifier_data['model']
        scaler = classifier_data['scaler']
        print("分類機読み込み完了")
        return True
    except Exception as e:
        print(f"分類機読み込みエラー: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mt_figures/<filename>')
def serve_histogram(filename):
    """
    ヒストグラム画像を提供
    """
    return send_from_directory('./mt_figures', filename)

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.json
        sequence = data.get('sequence', [])

        if not sequence:
            return jsonify({'error': '数列が空です'})

        if len(sequence) < 10:
            return jsonify({'error': '数列が短すぎます（最低10個必要）'})

        # 特徴量計算
        features = calculate_all_features(sequence)

        # 予測実行
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]

        # 人間判定の場合、詳細なランダム性分析を実行
        randomness_analysis = None
        deviation_report = None

        if prediction == 1:  # 人間判定の場合
            try:
                # 統計メトリクスを抽出してランダム性チェック
                stat_metrics = extract_statistical_metrics(features)
                randomness_analysis = check_sequence_randomness(stat_metrics)
                deviation_report = generate_deviation_report(randomness_analysis, stat_metrics)
            except Exception as e:
                print(f"Randomness analysis error: {e}")

        # 結果を返す
        result = {
            'success': True,
            'result': {
                'isHuman': bool(prediction == 1),
                'isMachineRandom': bool(prediction == 0),
                'verdict': 'human' if prediction == 1 else 'machine',
                'humanProbability': float(probabilities[1]),
                'machineProbability': float(probabilities[0]),
                'confidence': float(max(probabilities)),
                'rawPrediction': int(prediction)
            },
            'details': {
                'inputLength': len(sequence),
                'featuresCount': len(features.columns),
                'modelVersion': 'Python 527-feature classifier',
                'accuracy': '98.31%'
            },
            'feedback': generate_feedback(prediction == 1, max(probabilities)),
            'recommendations': generate_recommendations(prediction == 1),
            'randomnessAnalysis': randomness_analysis,
            'deviationReport': deviation_report
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'分類エラー: {str(e)}'})

def generate_feedback(is_human, confidence):
    feedback = []

    if is_human:
        if confidence > 0.8:
            feedback.append('🔍 明らかに人間が生成したパターンが検出されました')
            feedback.append('人間特有の認知バイアスや無意識のパターンが強く現れています')
        elif confidence > 0.6:
            feedback.append('👤 人間らしい特徴が見られます')
            feedback.append('いくつかの人間的なパターンが検出されました')
        else:
            feedback.append('❓ わずかに人間らしい傾向が見られます')
            feedback.append('機械的ランダム性に近いですが、微細な人間的特徴があります')
    else:
        if confidence > 0.8:
            feedback.append('🎉 素晴らしい！メルセンヌツイスター級のランダム性です！')
            feedback.append('機械的な真乱数生成器と同等の高品質な無作為性を実現しています')
        elif confidence > 0.6:
            feedback.append('✨ 優れたランダム性を示しています')
            feedback.append('わずかな人間的特徴はありますが、全体的に良好な無作為性です')
        else:
            feedback.append('⚖️ 機械的ランダム性に近い結果です')
            feedback.append('人間的な特徴も含まれていますが、比較的良好な無作為性です')

    return feedback

def generate_recommendations(is_human):
    recommendations = []

    if is_human:
        recommendations.extend([
            '🎯 より真のランダムに近づけるためのアドバイス:',
            '',
            '📋 基本原則:',
            '• 意識的にパターンを避けようとしすぎないでください',
            '• 各数字を等頻度で使おうと意識しすぎないでください',
            '• 前に選んだ数字のことは忘れて、純粋に直感で選んでください',
            '• 「ランダムっぽく見える」数列を作ろうとしないでください',
            '',
            '💡 実践的なヒント:',
            '• 目を閉じて、頭に浮かんだ数字をそのまま入力する',
            '• 時計の秒数やランダムな環境音を参考にする',
            '• サイコロやコインなどの物理的ランダム性を活用する'
        ])
    else:
        recommendations.extend([
            '🏆 おめでとうございます！',
            'あなたの数列は機械的な真乱数生成器に匹敵する高品質なランダム性を実現しています。',
            '',
            '✨ この成果の意味:',
            '• 人間の直感的ランダム性として非常に優秀です',
            '• 統計的に有意な偏りやパターンがほとんど検出されませんでした',
            '• このレベルの無作為性を一貫して維持するのは極めて困難です'
        ])

    return recommendations

def extract_statistical_metrics(features):
    """
    527特徴量から統計メトリクス（27個）を抽出してchecker用に変換
    """
    # 特徴量DataFrameから統計メトリクスを抽出
    metrics = {}

    # 基本統計量
    if 'redundancy' in features.columns:
        metrics['redundancy'] = float(features['redundancy'].iloc[0])
    if 'coupon_mean' in features.columns:
        metrics['coupon_mean'] = float(features['coupon_mean'].iloc[0])
    if 'coupon_std' in features.columns:
        metrics['coupon_std'] = float(features['coupon_std'].iloc[0])
    if 'repetition_gap_mean' in features.columns:
        metrics['repetition_gap_mean'] = float(features['repetition_gap_mean'].iloc[0])
    if 'repetition_gap_std' in features.columns:
        metrics['repetition_gap_std'] = float(features['repetition_gap_std'].iloc[0])
    if 'adjacent' in features.columns:
        metrics['adjacent'] = float(features['adjacent'].iloc[0])
    if 'tpi' in features.columns:
        metrics['tpi'] = float(features['tpi'].iloc[0])
    if 'autocorr_lag1' in features.columns:
        metrics['autocorr_lag1'] = float(features['autocorr_lag1'].iloc[0])
    if 'adjacent_diff_mean' in features.columns:
        metrics['adjacent_diff_mean'] = float(features['adjacent_diff_mean'].iloc[0])
    if 'adjacent_diff_std' in features.columns:
        metrics['adjacent_diff_std'] = float(features['adjacent_diff_std'].iloc[0])
    if 'max_min_ratio' in features.columns:
        metrics['max_min_ratio'] = float(features['max_min_ratio'].iloc[0])
    if 'rp' in features.columns:
        metrics['rp'] = float(features['rp'].iloc[0])

    # ポーカーテスト
    for i in range(1, 6):
        col = f'pl{i}'
        if col in features.columns:
            metrics[col] = float(features[col].iloc[0])

    # 頻度
    for i in range(10):
        col = f'freq_{i}'
        if col in features.columns:
            metrics[col] = float(features[col].iloc[0])

    return metrics

def generate_deviation_report(randomness_analysis, stat_metrics):
    """
    ランダム性分析結果から詳細な逸脱レポートを生成
    """
    if not randomness_analysis:
        return None

    # 境界値データを読み込み
    bounds_df = load_bounds_table()

    report = {
        'summary': {
            'total_metrics': len(stat_metrics),
            'outliers_count': len(randomness_analysis.get('outliers', [])),
            'within_bounds_count': len(randomness_analysis.get('within_bounds', [])),
            'is_random': len(randomness_analysis.get('outliers', [])) == 0
        },
        'outliers': [],
        'improvements': []
    }

    # 外れ値の詳細分析
    for outlier in randomness_analysis.get('outliers', []):
        metric_name = outlier['metric']
        actual_value = outlier['value']

        # 統計的期待範囲を計算
        expected_range = calculate_statistical_range(metric_name, bounds_df)

        outlier_info = {
            'metric': metric_name,
            'actual': actual_value,
            'expected_min': expected_range.get('lower'),
            'expected_max': expected_range.get('upper'),
            'expected_mean': expected_range.get('mean'),
            'deviation_type': 'high' if actual_value > expected_range.get('upper', float('inf')) else 'low',
            'explanation': get_metric_explanation(metric_name),
            'improvement_tip': get_improvement_tip(metric_name, actual_value, expected_range),
            'histogram_url': f'/mt_figures/{metric_name}_histogram.png',
            'detailed_explanation': get_detailed_metric_explanation(metric_name)
        }
        report['outliers'].append(outlier_info)

    # 改善提案の生成
    report['improvements'] = generate_improvement_suggestions(report['outliers'])

    return report

def load_bounds_table():
    """
    境界値テーブルを読み込み
    """
    try:
        bounds_path = './checker/mt_randomness_bounds.csv'
        return pd.read_csv(bounds_path)
    except FileNotFoundError:
        print("Warning: bounds table not found")
        return None

def calculate_statistical_range(metric_name, bounds_df, confidence_level=0.95):
    """
    統計的期待範囲を計算（正規分布仮定での信頼区間）
    """
    if bounds_df is None:
        return {'lower': None, 'upper': None, 'mean': None}

    metric_row = bounds_df[bounds_df['metric'] == metric_name]
    if metric_row.empty:
        return {'lower': None, 'upper': None, 'mean': None}

    row = metric_row.iloc[0]
    mean = row['expected_mean']
    std = row['expected_std']

    # 正規分布を仮定して信頼区間を計算
    if confidence_level == 0.95:
        # 95%信頼区間 (±1.96σ)
        z_score = 1.96
    elif confidence_level == 0.99:
        # 99%信頼区間 (±2.58σ)
        z_score = 2.58
    else:
        # デフォルト95%
        z_score = 1.96

    # 一部の指標は正規分布でない可能性があるので、平均値のみ使用
    non_normal_metrics = ['pl3', 'pl4', 'pl5', 'max_min_ratio']

    if metric_name in non_normal_metrics:
        # 非正規分布: 平均値のみ
        return {
            'lower': mean,
            'upper': mean,
            'mean': mean
        }
    else:
        # 正規分布仮定: 信頼区間を計算
        margin = z_score * std
        return {
            'lower': mean - margin,
            'upper': mean + margin,
            'mean': mean
        }

def get_metric_explanation(metric_name):
    """
    メトリクス名に基づいて簡潔な説明を返す
    """
    explanations = {
        'redundancy': '冗長性（情報の予測可能性）',
        'coupon_mean': 'クーポンコレクター平均（全数字収集効率）',
        'coupon_std': 'クーポンコレクター標準偏差（収集安定性）',
        'repetition_gap_mean': '繰り返し間隔平均（同数字再出現間隔）',
        'repetition_gap_std': '繰り返し間隔標準偏差（間隔のばらつき）',
        'adjacent': '隣接順序スコア（連続パターン頻度）',
        'tpi': 'ターニングポイント指数（増減転換点頻度）',
        'autocorr_lag1': '1次自己相関（前数字との関連性）',
        'adjacent_diff_mean': '隣接差分平均（隣接数字の差）',
        'adjacent_diff_std': '隣接差分標準偏差（差のばらつき）',
        'max_min_ratio': '最大最小頻度比（数字使用の偏り）',
        'rp': 'リピートパターン指標（同一パターン繰り返し）',
        'pl1': 'フェーズ長1（ターニングポイント間距離1）',
        'pl2': 'フェーズ長2（ターニングポイント間距離2）',
        'pl3': 'フェーズ長3（ターニングポイント間距離3）',
        'pl4': 'フェーズ長4（ターニングポイント間距離4）',
        'pl5': 'フェーズ長5（ターニングポイント間距離5）',
    }

    # 頻度系の説明
    for i in range(10):
        explanations[f'freq_{i}'] = f'数字{i}の出現頻度（理想は10%）'

    return explanations.get(metric_name, f'{metric_name}の統計的指標')

def get_detailed_metric_explanation(metric_name):
    """
    メトリクスの詳細説明を返す
    """
    detailed_explanations = {
        'redundancy': {
            'title': '冗長性 (Redundancy)',
            'description': 'シャノンのエントロピー理論に基づく指標で、乱数列がどれだけ冗長（予測可能）であるかを測定します。',
            'formula': '1 - (実際のエントロピー / 最大エントロピー)',
            'range': '0.0 〜 1.0',
            'interpretation': '0.0: 完全にランダム（理想的） / 1.0: 完全に予測可能'
        },
        'coupon_mean': {
            'title': 'クーポンコレクター問題 (Coupon Collector)',
            'description': '全ての数字（0〜9）を少なくとも1回ずつ集めるために必要な連続した数字の平均個数を測定します。',
            'formula': '各位置から始めて全ての数字が出現するまでの長さの平均',
            'range': '理論的最小値は約29.29',
            'interpretation': '小さい値（〜30）: ランダム性が高い / 大きい値（50以上）: 特定数字が出現しにくい'
        },
        'repetition_gap_mean': {
            'title': '繰り返し間隔 (Repetition Gap)',
            'description': '同じ数字が再び出現するまでの平均間隔を測定します。',
            'formula': '同じ数字の連続する出現位置の差の平均',
            'range': '1.0〜10.0',
            'interpretation': '10に近い値: ランダム性が高い / 小さい値: 同じ数字が頻繁に近接出現'
        },
        'adjacent': {
            'title': '隣接順序スコア (Adjacent Order Score)',
            'description': '連続する数字が+1または-1の差を持つ頻度を測定します。',
            'formula': '(n+1またはn-1の隣接ペア数) / (全ペア数)',
            'range': '0.0 〜 1.0',
            'interpretation': '高い値: 連続パターンが多い（1,2,3...） / 低い値: 隣接数値の連続性が少ない'
        },
        'tpi': {
            'title': 'ターニングポイントインデックス (Turning Point Index)',
            'description': '数列が増加から減少、または減少から増加に切り替わる頻度を測定します。',
            'formula': '実際のターニングポイント数 / 期待ターニングポイント数',
            'range': '0.0以上（理想的には1.0付近）',
            'interpretation': '1.0付近: ランダム列と同等 / >1.0: 振動が多い / <1.0: 傾向が続く'
        },
        'autocorr_lag1': {
            'title': '自己相関 (Lag-1 Autocorrelation)',
            'description': '数列内の各値とその直前の値との間の線形関係を測定します。',
            'formula': 'ラグ1の自己相関係数',
            'range': '-1.0 〜 1.0',
            'interpretation': '0に近い: 前後の数字に相関なし（理想的） / 正値: 似た傾向 / 負値: 逆の傾向'
        },
        'max_min_ratio': {
            'title': '最大・最小頻度比 (Max-Min Frequency Ratio)',
            'description': '数列内での各数字の出現頻度の最大値と最小値の比率を測定します。',
            'formula': '最頻出数字の頻度 / 最少出現数字の頻度',
            'range': '1.0以上',
            'interpretation': '1.0に近い: 全数字が均等出現（理想的） / 大きい値: 極端な偏りあり'
        },
        'rp': {
            'title': 'リピートパターン指標 (Repeat Pattern)',
            'description': '隣接2文字ペア（バイグラム）が繰り返し出現する度合いを測定します。',
            'formula': '1 - (一度しか現れないバイグラム数 / 全バイグラム数)',
            'range': '0.0 〜 1.0',
            'interpretation': '低い値: パターン繰り返し少なくランダム性高い / 高い値: パターン繰り返し多い'
        }
    }

    # フェーズ長系の詳細説明
    for i in range(1, 6):
        detailed_explanations[f'pl{i}'] = {
            'title': f'フェーズ長指標 {i} (Phase Length {i})',
            'description': f'ターニングポイント間の距離が{i}である場合の出現頻度を測定します。',
            'formula': f'観測されたフェーズ長{i} / 期待フェーズ長{i}',
            'range': '0.0以上（理想的には1.0付近）',
            'interpretation': f'1.0付近: ランダム列と同等 / >1.0: 距離{i}のTPが過剰 / <1.0: 距離{i}のTPが不足'
        }

    # 頻度系の詳細説明
    for i in range(10):
        detailed_explanations[f'freq_{i}'] = {
            'title': f'数字{i}の出現頻度 (Digit {i} Frequency)',
            'description': f'数字{i}の正規化された出現頻度を測定します。',
            'formula': f'数字{i}の出現回数 / 数列の長さ',
            'range': '0.0 〜 1.0',
            'interpretation': '理想的なランダムでは0.1（10%）で出現。偏りがあると高低が生じる'
        }

    return detailed_explanations.get(metric_name, {
        'title': metric_name,
        'description': '統計的指標',
        'formula': 'N/A',
        'range': 'N/A',
        'interpretation': 'N/A'
    })

def get_improvement_tip(metric_name, actual_value, expected_range):
    """
    具体的な改善提案を生成
    """
    if metric_name.startswith('freq_'):
        digit = metric_name.split('_')[1]
        if actual_value > expected_range.get('upper', 0.12):
            return f'数字{digit}を{actual_value*100:.1f}%使用（理想10%）。無意識に好む数字を避け、他の数字も意識的に選んでください'
        else:
            return f'数字{digit}を{actual_value*100:.1f}%しか使用（理想10%）。この数字を避ける傾向があります。意識的に使ってください'

    elif metric_name == 'redundancy':
        if actual_value > expected_range.get('upper', 0.02):
            return '情報が予測可能すぎます。規則性やパターンを意識せず、純粋に思い浮かんだ数字を選んでください'

    elif metric_name == 'adjacent':
        if actual_value > expected_range.get('upper', 0.25):
            return '連続する数字（1→2、7→6など）を多用しています。数字を選ぶ時に前の数字を無視してください'

    elif metric_name == 'autocorr_lag1':
        if abs(actual_value) > 0.15:
            direction = '大きい数字の後に大きい数字' if actual_value > 0 else '大きい数字の後に小さい数字'
            return f'前の数字との相関が強すぎます（{direction}を選ぶ傾向）。前の数字を完全に忘れて次を選んでください'

    elif metric_name == 'tpi':
        if actual_value > expected_range.get('upper', 1.1):
            return 'ターニングポイント（増減転換）が多すぎます。意図的な上下変動を避け、自然に数字を選んでください'
        elif actual_value < expected_range.get('lower', 0.8):
            return 'ターニングポイントが少なすぎます。一定方向への傾向が強いので、もっと変化をつけてください'

    elif metric_name == 'max_min_ratio':
        if actual_value > expected_range.get('upper', 2.5):
            return '特定の数字に偏りすぎています。嫌いな数字や好きな数字を意識せず、すべての数字を均等に使ってください'

    elif metric_name == 'rp':
        if actual_value > expected_range.get('upper', 1.05):
            return '同じ数字ペアを繰り返しすぎています。直前の2桁を忘れて、完全に新しい数字を選んでください'

    elif metric_name.startswith('pl'):
        phase_num = metric_name[2]
        if actual_value > expected_range.get('upper', 1.2):
            return f'フェーズ長{phase_num}の周期パターンが過剰です。{phase_num}個ごとの規則性を避け、完全にランダムに選んでください'

    elif metric_name in ['coupon_mean', 'coupon_std']:
        if 'mean' in metric_name and actual_value > expected_range.get('upper', 35):
            return '全数字の収集が非効率です。嫌いな数字や避けがちな数字を意識的に使ってください'
        elif 'std' in metric_name and actual_value > expected_range.get('upper', 15):
            return '数字収集の安定性が低いです。特定の数字を集中的に使わず、バランスよく選んでください'

    elif metric_name.startswith('repetition_gap'):
        if 'mean' in metric_name and actual_value < expected_range.get('lower', 8):
            return '同じ数字を近くで繰り返しすぎています。一度使った数字をしばらく避ける必要はありません'

    elif metric_name.startswith('adjacent_diff'):
        if 'mean' in metric_name and actual_value < expected_range.get('lower', 3.0):
            return '隣接する数字の差が小さすぎます。近い数字ばかり選ばず、離れた数字も選んでください'

    return '各数字を平等に扱い、前の選択を忘れて純粋にランダムに選んでください'

def generate_improvement_suggestions(outliers):
    """
    外れ値情報から総合的な改善提案を生成
    """
    suggestions = []

    # 頻度の偏りチェック
    freq_outliers = [o for o in outliers if o['metric'].startswith('freq_')]
    if len(freq_outliers) > 3:
        favorite_digits = [o['metric'].split('_')[1] for o in freq_outliers if o['deviation_type'] == 'high']
        avoided_digits = [o['metric'].split('_')[1] for o in freq_outliers if o['deviation_type'] == 'low']

        suggestion = '🎯 数字の使用に強い偏りがあります。'
        if favorite_digits:
            suggestion += f' 数字{",".join(favorite_digits)}を多用し、'
        if avoided_digits:
            suggestion += f' 数字{",".join(avoided_digits)}を避ける傾向があります。'
        suggestion += ' 好き嫌いを意識せず、全ての数字を平等に扱ってください。'
        suggestions.append(suggestion)

    # パターンと規則性チェック
    pattern_outliers = [o for o in outliers if o['metric'] in ['adjacent', 'rp', 'pl1', 'pl2', 'pl3']]
    if len(pattern_outliers) >= 2:
        suggestions.append('🔄 複数の規則的パターンが検出されています。「ランダムらしく見せよう」と意識せず、純粋に頭に浮かんだ数字をそのまま入力してください。')

    # 相関と依存性チェック
    dependency_outliers = [o for o in outliers if o['metric'] in ['autocorr_lag1', 'adjacent', 'repetition_gap_mean']]
    if len(dependency_outliers) >= 2:
        suggestions.append('🔗 前の選択が次の選択に影響しています。数字を選ぶ時は、これまでに何を選んだかを完全に忘れ、毎回新鮮な気持ちで選んでください。')

    # 変動パターンチェック
    variation_outliers = [o for o in outliers if o['metric'] in ['tpi', 'adjacent_diff_mean', 'adjacent_diff_std']]
    if len(variation_outliers) >= 2:
        suggestions.append('📊 数字の変動パターンに偏りがあります。意図的に大きく変化させたり、似た数字を続けたりせず、自然な選択を心がけてください。')

    # 冗長性チェック
    if any(o['metric'] == 'redundancy' for o in outliers):
        suggestions.append('🎲 情報の予測可能性が高すぎます。戦略的に考えずに、コインを投げるような純粋な偶然性で数字を選んでください。')

    # 効率性チェック
    collection_outliers = [o for o in outliers if o['metric'].startswith('coupon')]
    if len(collection_outliers) > 0:
        suggestions.append('📦 数字の収集効率に問題があります。特定の数字を無意識に避けている可能性があります。嫌いな数字も意識的に使ってください。')

    # フェーズ長チェック
    phase_outliers = [o for o in outliers if o['metric'].startswith('pl')]
    if len(phase_outliers) >= 2:
        phases = [o['metric'][2] for o in phase_outliers]
        suggestions.append(f'🔢 フェーズ長{",".join(phases)}に周期的パターンがあります。{len(phases)}種類の周期性が検出されているので、より不規則な選択を心がけてください。')

    if not suggestions:
        suggestions.append('💡 統計的には軽微な偏りのみです。さらに改善するには、数字選択時に一切の意図や戦略を排除し、完全に無意識で選んでください。')

    return suggestions

if __name__ == '__main__':
    if not load_classifier():
        print("分類機の読み込みに失敗しました")
        sys.exit(1)

    print("サーバー起動中...")
    print("ブラウザで http://localhost:5000 にアクセスしてください")
    app.run(debug=True, host='0.0.0.0', port=5000)