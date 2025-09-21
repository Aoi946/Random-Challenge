class HumanVsMachineClassifier {
    constructor() {
        this.featureExtractor = new MLFeatureExtractor();

        // 訓練済みモデルの重要な特徴量の係数（簡略版）
        // 実際のモデルから上位特徴量のみを使用
        this.modelWeights = {
            // 統計的特徴量の係数
            'repetition_gap_std': 2.1943,
            'redundancy': 1.6156,
            'pl5': 1.1721,
            'pl3': 1.1146,
            'rp': 1.0870,
            'adjacent_diff_std': 1.0216,
            'pl4': 1.0045,
            'adjacent': 0.9014,
            'max_min_ratio': 0.8706,
            'freq_3': 0.7138,
            'coupon_std': 0.5365,
            'pl1': 0.5356,
            'freq_5': 0.5215,
            'freq_8': 0.4545,
            'freq_7': 0.4416,
            'adjacent_diff_mean': 0.4258,
            'freq_2': 0.4007,
            'freq_4': 0.3254,
            'autocorr_lag1': 0.3243,
            'coupon_mean': 0.3046,
            'repetition_gap_mean': 0.2694,
            'freq_6': 0.1850,
            'freq_1': 0.1803,
            'freq_0': 0.1802,
            'pl2': 0.1458,
            'tpi': 0.1230,
            'freq_9': 0.0796,

            // 主要な遷移確率の係数（最重要のもののみ）
            'step2_trans_6_to_6': 2.1726,
            'step3_trans_4_to_4': 2.1330,
            'step4_trans_7_to_7': 1.9341,
            'step2_trans_1_to_1': 1.9047,
            'step3_trans_2_to_2': 1.8832,
            'step2_trans_9_to_9': 1.8800,
            'step3_trans_9_to_9': 1.8785,
            'step4_trans_1_to_1': 1.8775,
            'step3_trans_6_to_6': 1.8732,
            'step2_trans_7_to_7': 1.8039,
            'step4_trans_9_to_9': 1.7909,
            'step4_trans_4_to_4': 1.7713,
            'step3_trans_8_to_8': 1.6822,
            'step2_trans_4_to_4': 1.6699,
            'step3_trans_3_to_3': 1.6111,
            'step2_trans_5_to_5': 1.6053
        };

        this.bias = -0.5; // モデルのバイアス項

        // 特徴量の正規化パラメータ（簡略版）
        this.featureScaling = {
            means: {},
            stds: {}
        };

        this.initializeScaling();
    }

    initializeScaling() {
        // 特徴量の正規化パラメータを初期化
        // 実際の値は訓練データから計算されるべきですが、
        // ここでは推定値を使用

        Object.keys(this.modelWeights).forEach(feature => {
            if (feature.startsWith('freq_')) {
                this.featureScaling.means[feature] = 0.1;
                this.featureScaling.stds[feature] = 0.03;
            } else if (feature.includes('trans_')) {
                this.featureScaling.means[feature] = 0.01;
                this.featureScaling.stds[feature] = 0.02;
            } else {
                // 統計的特徴量のデフォルト値
                this.featureScaling.means[feature] = 0.5;
                this.featureScaling.stds[feature] = 0.3;
            }
        });
    }

    async classify(numbers) {
        try {
            // 特徴量を抽出
            const features = this.featureExtractor.extractAllFeatures(numbers);

            // 予測スコアを計算
            const prediction = this.predict(features);

            // 結果を解釈
            const analysis = this.interpretPrediction(prediction, features, numbers);

            return analysis;
        } catch (error) {
            console.error('Classification error:', error);
            throw new Error('分類中にエラーが発生しました');
        }
    }

    predict(features) {
        let score = this.bias;

        // 重み付き特徴量の合計を計算
        Object.keys(this.modelWeights).forEach(featureName => {
            if (features[featureName] !== undefined) {
                // 特徴量を正規化
                const normalizedValue = this.normalizeFeature(featureName, features[featureName]);

                // 重みを適用
                score += this.modelWeights[featureName] * normalizedValue;
            }
        });

        // シグモイド関数を適用して確率に変換
        const probability = this.sigmoid(score);

        return {
            rawScore: score,
            probability: probability,
            isHuman: probability > 0.5,
            confidence: Math.abs(probability - 0.5) * 2
        };
    }

    normalizeFeature(featureName, value) {
        const mean = this.featureScaling.means[featureName] || 0;
        const std = this.featureScaling.stds[featureName] || 1;

        return std > 0 ? (value - mean) / std : value - mean;
    }

    sigmoid(x) {
        return 1 / (1 + Math.exp(-x));
    }

    interpretPrediction(prediction, features, numbers) {
        const isHuman = prediction.isHuman;
        const confidence = prediction.confidence;

        // 特徴量分析
        const featureAnalysis = this.analyzeFeatures(features);

        // 結果の解釈
        const interpretation = {
            result: {
                isHuman: isHuman,
                isMachineRandom: !isHuman,
                confidence: confidence,
                probability: prediction.probability,
                verdict: isHuman ? 'human' : 'machine'
            },
            details: {
                inputLength: numbers.length,
                rawScore: prediction.rawScore,
                topFeatures: featureAnalysis.topFeatures,
                warnings: featureAnalysis.warnings
            },
            feedback: this.generateFeedback(isHuman, confidence, featureAnalysis),
            recommendations: this.generateRecommendations(isHuman, featureAnalysis)
        };

        return interpretation;
    }

    analyzeFeatures(features) {
        const featureScores = [];
        const warnings = [];

        // 各特徴量の貢献度を計算
        Object.keys(this.modelWeights).forEach(featureName => {
            if (features[featureName] !== undefined) {
                const normalizedValue = this.normalizeFeature(featureName, features[featureName]);
                const contribution = this.modelWeights[featureName] * normalizedValue;

                featureScores.push({
                    name: featureName,
                    value: features[featureName],
                    normalizedValue: normalizedValue,
                    weight: this.modelWeights[featureName],
                    contribution: contribution
                });
            }
        });

        // 貢献度でソート
        featureScores.sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));

        // 警告の生成
        if (features['repetition_gap_std'] > 2.0) {
            warnings.push('反復パターンのばらつきが大きすぎます');
        }
        if (features['redundancy'] > 0.8) {
            warnings.push('情報の冗長性が高すぎます');
        }
        if (features['adjacent'] > 0.3) {
            warnings.push('隣接する数字のパターンが多すぎます');
        }

        return {
            topFeatures: featureScores.slice(0, 10),
            warnings: warnings
        };
    }

    generateFeedback(isHuman, confidence, featureAnalysis) {
        const feedback = [];

        if (isHuman) {
            if (confidence > 0.8) {
                feedback.push('明らかに人間が生成したパターンです');
            } else if (confidence > 0.6) {
                feedback.push('人間らしいパターンが検出されました');
            } else {
                feedback.push('わずかに人間らしい特徴が見られます');
            }
        } else {
            if (confidence > 0.8) {
                feedback.push('🎉 おめでとうございます！メルセンヌツイスター級のランダム性です！');
            } else if (confidence > 0.6) {
                feedback.push('良好なランダム性を示していますが、わずかなパターンが検出されました');
            } else {
                feedback.push('機械的なランダム性に近いですが、人間的な特徴もあります');
            }
        }

        // 主要な問題点を指摘
        featureAnalysis.warnings.forEach(warning => {
            feedback.push(warning);
        });

        return feedback;
    }

    generateRecommendations(isHuman, featureAnalysis) {
        const recommendations = [];

        if (isHuman) {
            recommendations.push('より真のランダムに近づけるためのヒント：');
            recommendations.push('• 意識的なパターンを避けようとせず、本当に無作為に選んでください');
            recommendations.push('• 各数字（0-9）を等頻度で使うことを意識しすぎないでください');
            recommendations.push('• 前の数字に影響されずに次の数字を選んでください');

            if (featureAnalysis.warnings.length > 0) {
                recommendations.push('特に以下の点を改善してください：');
                featureAnalysis.warnings.forEach(warning => {
                    recommendations.push(`• ${warning}`);
                });
            }
        } else {
            recommendations.push('素晴らしいランダム性です！');
            recommendations.push('このレベルの無作為性を維持するのは非常に困難です');
        }

        return recommendations;
    }
}