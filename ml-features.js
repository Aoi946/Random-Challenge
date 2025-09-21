class MLFeatureExtractor {
    constructor() {
        this.statisticalFeatures = [
            'repetition_gap_std', 'redundancy', 'pl5', 'pl3', 'rp',
            'adjacent_diff_std', 'pl4', 'adjacent', 'max_min_ratio',
            'freq_0', 'freq_1', 'freq_2', 'freq_3', 'freq_4', 'freq_5',
            'freq_6', 'freq_7', 'freq_8', 'freq_9',
            'coupon_std', 'pl1', 'adjacent_diff_mean', 'autocorr_lag1',
            'coupon_mean', 'repetition_gap_mean', 'pl2', 'tpi'
        ];
    }

    extractAllFeatures(numbers) {
        const features = {};

        // 統計的特徴量を抽出
        const statFeatures = this.extractStatisticalFeatures(numbers);
        Object.assign(features, statFeatures);

        // 遷移確率特徴量を抽出（1-4ステップ）
        for (let step = 1; step <= 4; step++) {
            const transFeatures = this.extractTransitionFeatures(numbers, step);
            Object.assign(features, transFeatures);
        }

        return features;
    }

    extractStatisticalFeatures(numbers) {
        const features = {};
        const digits = numbers.map(n => parseInt(n));

        // 数字の出現頻度 (freq_0 to freq_9)
        const frequencies = this.calculateFrequencies(digits);
        for (let i = 0; i < 10; i++) {
            features[`freq_${i}`] = frequencies[i];
        }

        // 最大・最小頻度比
        const maxFreq = Math.max(...frequencies);
        const minFreq = Math.min(...frequencies.filter(f => f > 0));
        features['max_min_ratio'] = minFreq > 0 ? maxFreq / minFreq : maxFreq;

        // 隣接数字の差の統計
        const adjacentDiffs = this.calculateAdjacentDifferences(digits);
        features['adjacent_diff_mean'] = this.mean(adjacentDiffs);
        features['adjacent_diff_std'] = this.std(adjacentDiffs);

        // 隣接数字のカウント
        features['adjacent'] = this.countAdjacentPairs(digits);

        // 自己相関 (lag=1)
        features['autocorr_lag1'] = this.calculateAutocorrelation(digits, 1);

        // パターン長 (pl1 to pl5)
        for (let length = 1; length <= 5; length++) {
            features[`pl${length}`] = this.calculatePatternLength(digits, length);
        }

        // 反復パターン (rp)
        features['rp'] = this.calculateRepetitionPattern(digits);

        // 冗長性 (redundancy)
        features['redundancy'] = this.calculateRedundancy(digits);

        // 反復ギャップ統計
        const repetitionGaps = this.calculateRepetitionGaps(digits);
        features['repetition_gap_mean'] = this.mean(repetitionGaps);
        features['repetition_gap_std'] = this.std(repetitionGaps);

        // クーポンコレクター統計
        const couponStats = this.calculateCouponCollector(digits);
        features['coupon_mean'] = couponStats.mean;
        features['coupon_std'] = couponStats.std;

        // TPI (Turning Point Index)
        features['tpi'] = this.calculateTPI(digits);

        return features;
    }

    extractTransitionFeatures(numbers, step) {
        const features = {};
        const digits = numbers.map(n => parseInt(n));

        if (digits.length <= step) {
            // 数列が短すぎる場合は0で初期化
            for (let i = 0; i < 10; i++) {
                for (let j = 0; j < 10; j++) {
                    features[`step${step}_trans_${i}_to_${j}`] = 0;
                }
            }
            return features;
        }

        // 遷移カウントを初期化
        const transitionCounts = Array(10).fill(null).map(() => Array(10).fill(0));
        let totalTransitions = 0;

        // ステップ間隔での遷移をカウント
        for (let i = 0; i < digits.length - step; i++) {
            const from = digits[i];
            const to = digits[i + step];
            transitionCounts[from][to]++;
            totalTransitions++;
        }

        // 確率に変換
        for (let i = 0; i < 10; i++) {
            for (let j = 0; j < 10; j++) {
                const probability = totalTransitions > 0 ?
                    transitionCounts[i][j] / totalTransitions : 0;
                features[`step${step}_trans_${i}_to_${j}`] = probability;
            }
        }

        return features;
    }

    calculateFrequencies(digits) {
        const frequencies = Array(10).fill(0);
        digits.forEach(digit => frequencies[digit]++);
        return frequencies.map(count => count / digits.length);
    }

    calculateAdjacentDifferences(digits) {
        const diffs = [];
        for (let i = 0; i < digits.length - 1; i++) {
            diffs.push(Math.abs(digits[i + 1] - digits[i]));
        }
        return diffs;
    }

    countAdjacentPairs(digits) {
        let count = 0;
        for (let i = 0; i < digits.length - 1; i++) {
            if (Math.abs(digits[i + 1] - digits[i]) === 1) {
                count++;
            }
        }
        return count / Math.max(1, digits.length - 1);
    }

    calculateAutocorrelation(digits, lag) {
        if (digits.length <= lag) return 0;

        const mean = this.mean(digits);
        let numerator = 0;
        let denominator = 0;

        for (let i = 0; i < digits.length - lag; i++) {
            numerator += (digits[i] - mean) * (digits[i + lag] - mean);
        }

        for (let i = 0; i < digits.length; i++) {
            denominator += Math.pow(digits[i] - mean, 2);
        }

        return denominator > 0 ? numerator / denominator : 0;
    }

    calculatePatternLength(digits, length) {
        const patterns = new Set();
        for (let i = 0; i <= digits.length - length; i++) {
            const pattern = digits.slice(i, i + length).join('');
            patterns.add(pattern);
        }
        return patterns.size / Math.max(1, digits.length - length + 1);
    }

    calculateRepetitionPattern(digits) {
        let repetitions = 0;
        for (let i = 0; i < digits.length - 1; i++) {
            if (digits[i] === digits[i + 1]) {
                repetitions++;
            }
        }
        return repetitions / Math.max(1, digits.length - 1);
    }

    calculateRedundancy(digits) {
        const frequencies = this.calculateFrequencies(digits);
        let entropy = 0;
        frequencies.forEach(freq => {
            if (freq > 0) {
                entropy -= freq * Math.log2(freq);
            }
        });
        const maxEntropy = Math.log2(10);
        return maxEntropy > 0 ? 1 - (entropy / maxEntropy) : 0;
    }

    calculateRepetitionGaps(digits) {
        const gaps = [];
        const lastSeen = {};

        digits.forEach((digit, index) => {
            if (lastSeen[digit] !== undefined) {
                gaps.push(index - lastSeen[digit]);
            }
            lastSeen[digit] = index;
        });

        return gaps.length > 0 ? gaps : [0];
    }

    calculateCouponCollector(digits) {
        const collections = [];
        const seen = new Set();
        let steps = 0;

        for (const digit of digits) {
            steps++;
            seen.add(digit);
            if (seen.size === 10) {
                collections.push(steps);
                seen.clear();
                steps = 0;
            }
        }

        return {
            mean: collections.length > 0 ? this.mean(collections) : digits.length,
            std: collections.length > 1 ? this.std(collections) : 0
        };
    }

    calculateTPI(digits) {
        if (digits.length < 3) return 0;

        let turningPoints = 0;
        for (let i = 1; i < digits.length - 1; i++) {
            const prev = digits[i - 1];
            const curr = digits[i];
            const next = digits[i + 1];

            if ((curr > prev && curr > next) || (curr < prev && curr < next)) {
                turningPoints++;
            }
        }

        return turningPoints / Math.max(1, digits.length - 2);
    }

    mean(array) {
        return array.length > 0 ? array.reduce((a, b) => a + b, 0) / array.length : 0;
    }

    std(array) {
        if (array.length <= 1) return 0;
        const avg = this.mean(array);
        const variance = array.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / (array.length - 1);
        return Math.sqrt(variance);
    }
}