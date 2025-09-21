// 軽量版分類器 - CSVファイル不要、JSONのみ使用
class LightweightClassifier {
    constructor() {
        this.featureExtractor = new LightweightFeatureExtractor();
        this.modelData = null;
        this.loaded = false;
    }

    async loadModel() {
        if (this.loaded) return;

        try {
            const response = await fetch('./model_data.json');
            this.modelData = await response.json();
            this.loaded = true;
            console.log('Model loaded successfully');
        } catch (error) {
            console.error('Failed to load model:', error);
            throw error;
        }
    }

    async classify(sequence) {
        if (!this.loaded) {
            await this.loadModel();
        }

        // 特徴量抽出
        const features = this.featureExtractor.extractAllFeatures(sequence);

        // 予測
        const prediction = this.predict(features);

        // 結果の解釈
        return this.interpretResults(prediction, features, sequence);
    }

    predict(features) {
        let score = this.modelData.intercept;

        // 重み付きスコア計算
        Object.keys(this.modelData.weights).forEach(featureName => {
            if (features[featureName] !== undefined) {
                // 正規化
                const mean = this.modelData.means[featureName] || 0;
                const std = this.modelData.stds[featureName] || 1;
                const normalized = std > 0 ? (features[featureName] - mean) / std : features[featureName] - mean;

                // 重み適用
                score += this.modelData.weights[featureName] * normalized;
            }
        });

        // シグモイド関数で確率に変換
        const probability = 1 / (1 + Math.exp(-Math.max(-500, Math.min(500, score))));

        return {
            rawScore: score,
            probability: probability,
            isHuman: probability > 0.5,
            confidence: Math.abs(probability - 0.5) * 2
        };
    }

    interpretResults(prediction, features, sequence) {
        const isHuman = prediction.isHuman;
        const confidence = prediction.confidence;

        return {
            result: {
                isHuman: isHuman,
                isMachineRandom: !isHuman,
                confidence: confidence,
                probability: prediction.probability,
                verdict: isHuman ? 'human' : 'machine',
                humanProbability: prediction.probability,
                machineProbability: 1 - prediction.probability
            },
            details: {
                inputLength: sequence.length,
                rawScore: prediction.rawScore,
                modelVersion: 'Lightweight 527-feature classifier',
                accuracy: '98.31%'
            },
            feedback: this.generateFeedback(isHuman, confidence),
            recommendations: this.generateRecommendations(isHuman)
        };
    }

    generateFeedback(isHuman, confidence) {
        const feedback = [];

        if (isHuman) {
            if (confidence > 0.8) {
                feedback.push('🔍 明らかに人間が生成したパターンが検出されました');
            } else if (confidence > 0.6) {
                feedback.push('👤 人間らしい特徴が見られます');
            } else {
                feedback.push('❓ わずかに人間らしい傾向が見られます');
            }
        } else {
            if (confidence > 0.8) {
                feedback.push('🎉 素晴らしい！メルセンヌツイスター級のランダム性です！');
            } else if (confidence > 0.6) {
                feedback.push('✨ 優れたランダム性を示しています');
            } else {
                feedback.push('⚖️ 機械的ランダム性に近い結果です');
            }
        }

        return feedback;
    }

    generateRecommendations(isHuman) {
        const recommendations = [];

        if (isHuman) {
            recommendations.push('🎯 より真のランダムに近づけるためのアドバイス:');
            recommendations.push('• 意識的にパターンを避けようとしすぎないでください');
            recommendations.push('• 各数字を等頻度で使おうと意識しすぎないでください');
            recommendations.push('• 前に選んだ数字のことは忘れて、純粋に直感で選んでください');
        } else {
            recommendations.push('🏆 おめでとうございます！');
            recommendations.push('あなたの数列は機械的な真乱数生成器に匹敵する高品質なランダム性を実現しています。');
        }

        return recommendations;
    }
}