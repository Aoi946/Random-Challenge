// 軽量版特徴量抽出器 - CSVファイル不要
class LightweightFeatureExtractor {
    extractAllFeatures(sequence) {
        const features = {};

        // 統計的特徴量
        const stats = this.calculateStatisticalFeatures(sequence);
        Object.assign(features, stats);

        // 遷移確率（1-5ステップ）
        for (let step = 1; step <= 5; step++) {
            const transitions = this.calculateTransitionProbabilities(sequence, step);
            Object.assign(features, transitions);
        }

        return features;
    }

    calculateStatisticalFeatures(sequence) {
        const features = {};
        const n = sequence.length;

        // 数字の頻度
        const freqs = new Array(10).fill(0);
        sequence.forEach(digit => freqs[digit]++);
        for (let i = 0; i < 10; i++) {
            features[`freq_${i}`] = freqs[i] / n;
        }

        // 冗長性 (Shannon entropy based)
        const entropy = -freqs.reduce((sum, f) => {
            const p = f / n;
            return sum + (p > 0 ? p * Math.log2(p) : 0);
        }, 0);
        features['redundancy'] = 1 - entropy / Math.log2(10);

        // 隣接差分
        const adjDiffs = [];
        for (let i = 1; i < n; i++) {
            adjDiffs.push(Math.abs(sequence[i] - sequence[i-1]));
        }
        features['adjacent_diff_mean'] = adjDiffs.reduce((a, b) => a + b, 0) / adjDiffs.length;
        features['adjacent_diff_std'] = this.standardDeviation(adjDiffs);

        // 隣接パターン
        let adjCount = 0;
        for (let i = 1; i < n; i++) {
            if (Math.abs(sequence[i] - sequence[i-1]) <= 1) adjCount++;
        }
        features['adjacent'] = adjCount / (n - 1);

        // 最大最小頻度比
        const maxFreq = Math.max(...freqs) / n;
        const minFreq = Math.min(...freqs) / n;
        features['max_min_ratio'] = minFreq > 0 ? maxFreq / minFreq : maxFreq;

        // 自己相関 (lag 1)
        const mean = sequence.reduce((a, b) => a + b, 0) / n;
        let num = 0, den = 0;
        for (let i = 0; i < n - 1; i++) {
            num += (sequence[i] - mean) * (sequence[i + 1] - mean);
        }
        for (let i = 0; i < n; i++) {
            den += Math.pow(sequence[i] - mean, 2);
        }
        features['autocorr_lag1'] = den > 0 ? num / den : 0;

        // TPI (Turning Point Index)
        let turningPoints = 0;
        for (let i = 1; i < n - 1; i++) {
            if ((sequence[i] > sequence[i-1] && sequence[i] > sequence[i+1]) ||
                (sequence[i] < sequence[i-1] && sequence[i] < sequence[i+1])) {
                turningPoints++;
            }
        }
        features['tpi'] = turningPoints / (n - 2);

        // 反復ギャップ
        const gaps = this.calculateRepetitionGaps(sequence);
        features['repetition_gap_mean'] = gaps.length > 0 ? gaps.reduce((a, b) => a + b, 0) / gaps.length : 0;
        features['repetition_gap_std'] = gaps.length > 0 ? this.standardDeviation(gaps) : 0;

        // クーポンコレクター
        const coupon = this.calculateCouponCollector(sequence);
        features['coupon_mean'] = coupon.mean;
        features['coupon_std'] = coupon.std;

        // ポーカーテスト
        const poker = this.calculatePokerTests(sequence);
        Object.assign(features, poker);

        // ランとパターン
        features['rp'] = this.calculateRunsAndPatterns(sequence);

        return features;
    }

    calculateTransitionProbabilities(sequence, step) {
        const transitions = {};
        const counts = {};

        // 初期化
        for (let i = 0; i < 10; i++) {
            for (let j = 0; j < 10; j++) {
                counts[`${i}_${j}`] = 0;
            }
        }

        // カウント
        for (let i = 0; i < sequence.length - step; i++) {
            const from = sequence[i];
            const to = sequence[i + step];
            counts[`${from}_${to}`]++;
        }

        // 確率に変換
        const total = sequence.length - step;
        for (let i = 0; i < 10; i++) {
            for (let j = 0; j < 10; j++) {
                const key = `step${step}_trans_${i}_to_${j}`;
                transitions[key] = total > 0 ? counts[`${i}_${j}`] / total : 0;
            }
        }

        return transitions;
    }

    calculateRepetitionGaps(sequence) {
        const gaps = [];
        const lastSeen = {};

        sequence.forEach((digit, index) => {
            if (lastSeen[digit] !== undefined) {
                gaps.push(index - lastSeen[digit]);
            }
            lastSeen[digit] = index;
        });

        return gaps;
    }

    calculateCouponCollector(sequence) {
        const collections = [];
        let collected = new Set();
        let steps = 0;

        for (const digit of sequence) {
            steps++;
            collected.add(digit);
            if (collected.size === 10) {
                collections.push(steps);
                collected.clear();
                steps = 0;
            }
        }

        if (collections.length === 0) {
            return { mean: sequence.length, std: 0 };
        }

        const mean = collections.reduce((a, b) => a + b, 0) / collections.length;
        const std = this.standardDeviation(collections);

        return { mean, std };
    }

    calculatePokerTests(sequence) {
        const features = {};

        for (let len = 1; len <= 5; len++) {
            const patterns = {};

            for (let i = 0; i <= sequence.length - len; i++) {
                const pattern = sequence.slice(i, i + len).join('');
                patterns[pattern] = (patterns[pattern] || 0) + 1;
            }

            const counts = Object.values(patterns);
            const total = counts.reduce((a, b) => a + b, 0);
            const expected = total / Math.pow(10, len);

            const chiSquare = counts.reduce((sum, count) => {
                return sum + Math.pow(count - expected, 2) / expected;
            }, 0);

            features[`pl${len}`] = chiSquare;
        }

        return features;
    }

    calculateRunsAndPatterns(sequence) {
        let runs = 0;
        let currentRun = 1;

        for (let i = 1; i < sequence.length; i++) {
            if (sequence[i] === sequence[i-1]) {
                currentRun++;
            } else {
                if (currentRun > 1) runs++;
                currentRun = 1;
            }
        }
        if (currentRun > 1) runs++;

        return runs / sequence.length;
    }

    standardDeviation(arr) {
        if (arr.length === 0) return 0;
        const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
        const variance = arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / arr.length;
        return Math.sqrt(variance);
    }
}