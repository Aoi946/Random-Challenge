class RandomChallenge {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.updateCounters();
    }

    initializeElements() {
        this.numberInput = document.getElementById('numberInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.generateSampleBtn = document.getElementById('generateSampleBtn');
        this.charCount = document.getElementById('charCount');
        this.numberCount = document.getElementById('numberCount');
        this.resultSection = document.getElementById('resultSection');
        this.resultContent = document.getElementById('resultContent');
        this.loadingSection = document.getElementById('loadingSection');
    }

    bindEvents() {
        this.numberInput.addEventListener('input', () => this.updateCounters());
        this.analyzeBtn.addEventListener('click', () => this.analyzeNumbers());
        this.clearBtn.addEventListener('click', () => this.clearInput());
        this.generateSampleBtn.addEventListener('click', () => this.generateSample());
    }

    updateCounters() {
        const text = this.numberInput.value;
        const numbers = this.extractNumbers(text);

        this.charCount.textContent = `${text.length}文字`;
        this.numberCount.textContent = `${numbers.length}個の数字`;

        this.analyzeBtn.disabled = numbers.length === 0;
    }

    extractNumbers(text) {
        return text.replace(/[^\d]/g, '').split('').filter(char => char !== '');
    }

    async analyzeNumbers() {
        const numbers = this.extractNumbers(this.numberInput.value);

        if (numbers.length === 0) {
            alert('数字を入力してください');
            return;
        }

        if (numbers.length < 10) {
            alert('より正確な分析のため、最低10個の数字を入力してください');
            return;
        }

        this.showLoading();

        try {
            await this.performAnalysis(numbers);
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('解析中にエラーが発生しました');
        }
    }

    async performAnalysis(numbers) {
        await new Promise(resolve => setTimeout(resolve, 2000));

        const analysis = this.analyzeRandomness(numbers);
        this.displayResults(analysis, numbers);
    }

    analyzeRandomness(numbers) {
        const stats = this.calculateBasicStats(numbers);
        const patterns = this.detectPatterns(numbers);
        const randomnessScore = this.calculateRandomnessScore(stats, patterns);

        return {
            stats,
            patterns,
            randomnessScore,
            isTrueRandom: randomnessScore > 0.7,
            feedback: this.generateFeedback(stats, patterns, randomnessScore)
        };
    }

    calculateBasicStats(numbers) {
        const digitCounts = Array(10).fill(0);
        numbers.forEach(num => digitCounts[parseInt(num)]++);

        const frequencies = digitCounts.map(count => count / numbers.length);
        const expectedFreq = 0.1;
        const chiSquare = frequencies.reduce((sum, freq) =>
            sum + Math.pow(freq - expectedFreq, 2) / expectedFreq, 0);

        return {
            length: numbers.length,
            digitCounts,
            frequencies,
            chiSquare,
            uniformity: 1 - (chiSquare / 9)
        };
    }

    detectPatterns(numbers) {
        const patterns = {
            sequential: this.countSequentialPatterns(numbers),
            repetition: this.countRepetitivePatterns(numbers),
            alternating: this.countAlternatingPatterns(numbers)
        };

        return patterns;
    }

    countSequentialPatterns(numbers) {
        let count = 0;
        for (let i = 0; i < numbers.length - 2; i++) {
            const a = parseInt(numbers[i]);
            const b = parseInt(numbers[i + 1]);
            const c = parseInt(numbers[i + 2]);

            if ((b === a + 1 && c === b + 1) || (b === a - 1 && c === b - 1)) {
                count++;
            }
        }
        return count;
    }

    countRepetitivePatterns(numbers) {
        let count = 0;
        for (let i = 0; i < numbers.length - 2; i++) {
            if (numbers[i] === numbers[i + 1] && numbers[i + 1] === numbers[i + 2]) {
                count++;
            }
        }
        return count;
    }

    countAlternatingPatterns(numbers) {
        let count = 0;
        for (let i = 0; i < numbers.length - 3; i++) {
            if (numbers[i] === numbers[i + 2] && numbers[i + 1] === numbers[i + 3] &&
                numbers[i] !== numbers[i + 1]) {
                count++;
            }
        }
        return count;
    }

    calculateRandomnessScore(stats, patterns) {
        let score = stats.uniformity * 0.5;

        const patternPenalty = (patterns.sequential + patterns.repetition + patterns.alternating) / stats.length;
        score -= patternPenalty * 0.3;

        score = Math.max(0, Math.min(1, score));
        return score;
    }

    generateFeedback(stats, patterns, score) {
        const feedback = [];

        if (score > 0.8) {
            feedback.push('優秀なランダム性を示しています！');
        } else if (score > 0.6) {
            feedback.push('まずまずのランダム性です。');
        } else {
            feedback.push('ランダム性が低く、パターンが検出されました。');
        }

        if (stats.uniformity < 0.7) {
            feedback.push('数字の分布に偏りが見られます。');
        }

        if (patterns.sequential > 0) {
            feedback.push(`${patterns.sequential}個の連続パターンが検出されました。`);
        }

        if (patterns.repetition > 0) {
            feedback.push(`${patterns.repetition}個の繰り返しパターンが検出されました。`);
        }

        return feedback;
    }

    displayResults(analysis, numbers) {
        const { stats, patterns, randomnessScore, isTrueRandom, feedback } = analysis;

        const resultHTML = `
            <div class="result-header ${isTrueRandom ? 'success' : 'warning'}">
                <div class="result-icon">${isTrueRandom ? '🎉' : '🤔'}</div>
                <h3>${isTrueRandom ? 'おめでとうございます！' : '残念ながら...'}</h3>
                <p class="result-verdict">
                    ${isTrueRandom ?
                        'あなたの数列は真乱数レベルのランダム性を示しています！' :
                        'あなたの数列にはパターンが検出されました。'}
                </p>
            </div>

            <div class="score-display">
                <div class="score-circle">
                    <div class="score-value">${Math.round(randomnessScore * 100)}</div>
                    <div class="score-label">ランダム度</div>
                </div>
            </div>

            <div class="analysis-details">
                <h4>詳細分析</h4>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">入力数字数</span>
                        <span class="stat-value">${stats.length}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">分布の均一性</span>
                        <span class="stat-value">${Math.round(stats.uniformity * 100)}%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">連続パターン</span>
                        <span class="stat-value">${patterns.sequential}個</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">繰り返しパターン</span>
                        <span class="stat-value">${patterns.repetition}個</span>
                    </div>
                </div>

                <div class="digit-distribution">
                    <h5>数字の分布</h5>
                    <div class="distribution-chart">
                        ${stats.digitCounts.map((count, digit) => `
                            <div class="digit-bar">
                                <div class="digit-label">${digit}</div>
                                <div class="bar-container">
                                    <div class="bar" style="height: ${(count / Math.max(...stats.digitCounts)) * 100}%"></div>
                                </div>
                                <div class="digit-count">${count}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="feedback">
                    <h5>フィードバック</h5>
                    <ul>
                        ${feedback.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            </div>

            <div class="action-buttons">
                <button onclick="app.tryAgain()" class="btn-primary">もう一度挑戦</button>
                <button onclick="app.generateAdvice()" class="btn-secondary">改善のヒント</button>
            </div>
        `;

        this.resultContent.innerHTML = resultHTML;
        this.hideLoading();
        this.showResults();
    }

    showLoading() {
        this.loadingSection.style.display = 'block';
        this.resultSection.style.display = 'none';
    }

    hideLoading() {
        this.loadingSection.style.display = 'none';
    }

    showResults() {
        this.resultSection.style.display = 'block';
        this.resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    showError(message) {
        this.hideLoading();
        alert(message);
    }

    clearInput() {
        this.numberInput.value = '';
        this.updateCounters();
        this.resultSection.style.display = 'none';
    }

    generateSample() {
        const sampleNumbers = [];
        for (let i = 0; i < 50; i++) {
            sampleNumbers.push(Math.floor(Math.random() * 10));
        }
        this.numberInput.value = sampleNumbers.join('');
        this.updateCounters();
    }

    tryAgain() {
        this.clearInput();
        this.numberInput.focus();
    }

    generateAdvice() {
        const advice = [
            "人間は無意識にパターンを作ってしまいがちです",
            "真にランダムな数列を作るには、コインやサイコロを使用してみてください",
            "連続した数字や繰り返しを避けようとしすぎると、逆にパターンになってしまいます",
            "各数字（0-9）が均等に現れるようにしつつ、順序をランダムにしてみてください"
        ];

        alert(advice.join('\n\n'));
    }
}

const app = new RandomChallenge();