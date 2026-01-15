// main.js - Typinger Web フロントエンド

class TypingerApp {
    constructor() {
        console.log('=== Typinger App Constructor Called ===');
        this.sessionId = null;
        this.currentScenario = null;
        this.typingStartTime = null;
        this.init();
    }

    init() {
        console.log('Initializing app...');
        this.loadScenarios();
        this.setupKeymapPresets();
        this.setupEventListeners();
        console.log('App initialization complete!');
    }

    // ========== キーマップ管理 ==========
    async setupKeymapPresets() {
        const presetButtons = document.querySelectorAll('.preset-btn');
        presetButtons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const preset = e.target.dataset.preset;
                await this.loadKeymapPreset(preset);
                
                // アクティブボタンを更新
                presetButtons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // デフォルトでJISをロード
        await this.loadKeymapPreset('jis');
        const jisBtn = document.querySelector('[data-preset="jis"]');
        if (jisBtn) jisBtn.classList.add('active');
    }

    async loadKeymapPreset(preset) {
        try {
            const response = await fetch(`/api/keymap/presets/${preset}`);
            const keymap = await response.json();
            
            // 現在のキーマップ表示を更新
            const presetNames = {
                'jis': 'JIS配列',
                'ansi': 'ANSI配列',
                'dvorak': 'Dvorak配列'
            };
            
            const currentKeymapEl = document.getElementById('current-keymap');
            if (currentKeymapEl) {
                currentKeymapEl.innerHTML = `<p>${presetNames[preset]}</p>`;
            }
            
            // ローカルストレージに保存
            localStorage.setItem('currentKeymap', JSON.stringify(keymap));
            localStorage.setItem('currentKeymapPreset', preset);
        } catch (error) {
            console.error('Error loading keymap preset:', error);
        }
    }

    // ========== シナリオ管理 ==========
    async loadScenarios() {
        try {
            console.log('Loading scenarios...');
            const response = await fetch('/api/scenarios');
            const data = await response.json();
            
            console.log('✓ Scenarios loaded:', data);
            
            if (data.ok && data.scenarios) {
                console.log(`✓ Found ${data.scenarios.length} scenarios`);
                this.displayScenarios(data.scenarios);
            } else {
                console.error('✗ Failed to load scenarios:', data.error);
                this.displayScenarios([]);
            }
        } catch (error) {
            console.error('✗ Error loading scenarios:', error);
            this.displayScenarios([]);
        }
    }

    displayScenarios(scenarios) {
        const scenarioList = document.getElementById('scenario-list');
        scenarioList.innerHTML = '';
        
        console.log('Displaying scenarios:', scenarios);
        
        if (!scenarios || scenarios.length === 0) {
            console.warn('⚠ No scenarios to display');
            scenarioList.innerHTML = `
                <div class="no-scenarios-message">
                    <p>📋 シナリオが見つかりません</p>
                    <p style="font-size: 12px; color: #7f8c8d; margin-top: 10px;">
                        <a href="/scenario-writer" style="color: #3498db; text-decoration: none;">📝 シナリオライターでシナリオを作成</a>
                    </p>
                </div>
            `;
            return;
        }
        
        scenarios.forEach((scenario, index) => {
            const item = document.createElement('div');
            item.className = 'scenario-item';
            item.setAttribute('role', 'button');
            item.setAttribute('tabindex', index);
            item.innerHTML = `
                <div class="scenario-header">
                    <h3 class="scenario-title">${scenario.title}</h3>
                    <div class="scenario-badge">${scenario.sentence_count || 0} 問</div>
                </div>
                <div class="scenario-info">
                    <p>📄 ファイル: <code>${scenario.filename}</code></p>
                </div>
                <button class="btn btn-scenario-play" aria-label="このシナリオでタイピング開始">
                    <span class="btn-icon">▶</span>
                    <span class="btn-text">タイピング開始</span>
                </button>
            `;
            
            // ボタンをクリック
            const btn = item.querySelector('.btn-scenario-play');
            const handleStart = () => this.startSession(scenario.filename);
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                handleStart();
            });
            
            // Enterキーでも開始
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleStart();
                }
            });
            
            // カード全体をクリック
            item.addEventListener('click', handleStart);
            
            scenarioList.appendChild(item);
        });
        
        console.log(`✓ Rendered ${scenarios.length} scenario cards`);
    }

    // ========== セッション管理 ==========
    async startSession(scenarioFile) {
        try {
            const response = await fetch('/api/session/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scenario_file: scenarioFile })
            });
            const data = await response.json();
            
            if (data.ok) {
                this.sessionId = data.session_id;
                this.currentScenario = scenarioFile;
                this.typingStartTime = Date.now();
                this.displayTypingScreen(data.target_text, data.target_rubi);
            } else {
                alert('セッション開始エラー: ' + data.error);
            }
        } catch (error) {
            console.error('Error starting session:', error);
            alert('セッション開始に失敗しました');
        }
    }

    displayTypingScreen(targetText, targetRubi) {
        // 画面を切り替え
        this.switchScreen('typing-screen');
        
        // テキストを表示
        document.getElementById('target-text').textContent = targetText;
        document.getElementById('rubi-remaining').textContent = targetRubi;
        
        // 入力フィールドにフォーカス
        const input = document.getElementById('typing-input');
        input.value = '';
        input.focus();
    }

    // ========== タイピング処理 ==========
    setupEventListeners() {
        const input = document.getElementById('typing-input');
        const finishBtn = document.getElementById('btn-finish');
        const escapeBtn = document.getElementById('btn-escape');
        const retryBtn = document.getElementById('btn-retry');
        const homeBtn = document.getElementById('btn-home');

        input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        finishBtn.addEventListener('click', () => this.finishSession());
        escapeBtn.addEventListener('click', () => this.escapeSession());
        retryBtn.addEventListener('click', () => this.handleRetry());
        homeBtn.addEventListener('click', () => this.handleHome());
    }

    async handleKeyDown(event) {
        if (!this.sessionId) return;

        const char = event.key;

        // Backspace処理
        if (event.key === 'Backspace') {
            event.preventDefault();
            await this.handleBackspace();
            return;
        }

        // 制御文字は無視
        if (event.ctrlKey || event.altKey || event.metaKey) return;

        // 通常のキー入力を判定
        const timestamp = Date.now() - this.typingStartTime;

        try {
            const response = await fetch(`/api/session/${this.sessionId}/judge_char`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ char: char, timestamp: timestamp })
            });
            const data = await response.json();

            if (data.ok) {
                this.updateDisplay(data.progress);

                // 完了判定
                if (data.progress.is_completed) {
                    setTimeout(() => this.finishSession(), 500);
                }
            }
        } catch (error) {
            console.error('Error judging character:', error);
        }
    }

    async handleBackspace() {
        if (!this.sessionId) return;

        const timestamp = Date.now() - this.typingStartTime;

        try {
            const response = await fetch(`/api/session/${this.sessionId}/backspace`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timestamp: timestamp })
            });
            const data = await response.json();

            if (data.ok) {
                this.updateDisplay(data.progress);
            }
        } catch (error) {
            console.error('Error handling backspace:', error);
        }
    }

    updateDisplay(progress) {
        // ローマ字表示の更新
        const targetRubi = progress.target_rubi;
        const currentPos = progress.current_position;

        const completed = targetRubi.substring(0, currentPos);
        const current = currentPos < targetRubi.length ? targetRubi[currentPos] : '';
        const remaining = targetRubi.substring(currentPos + 1);

        document.getElementById('rubi-completed').textContent = completed;
        document.getElementById('rubi-current').textContent = current;
        document.getElementById('rubi-remaining').textContent = remaining;

        // 統計情報の更新
        document.getElementById('stat-correct').textContent = progress.correct_count;
        document.getElementById('stat-incorrect').textContent = progress.incorrect_count;
        document.getElementById('stat-accuracy').textContent = 
            (progress.accuracy * 100).toFixed(1) + '%';
        document.getElementById('stat-progress').textContent = 
            progress.progress_percent.toFixed(1) + '%';

        // 入力フィールドをクリア
        document.getElementById('typing-input').value = '';
    }

    // ========== セッション完了 ==========
    async finishSession() {
        if (!this.sessionId) return;

        try {
            const response = await fetch(`/api/session/${this.sessionId}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (data.ok) {
                this.displayStatistics(data.statistics, data.files);
            } else {
                alert('セッション完了エラー: ' + data.error);
            }
        } catch (error) {
            console.error('Error completing session:', error);
            alert('セッション完了に失敗しました');
        }
    }

    displayStatistics(statistics, files) {
        // 画面を切り替え
        this.switchScreen('statistics-screen');

        // 統計情報を表示
        document.getElementById('result-duration').textContent = 
            (statistics.total_duration_ms / 1000).toFixed(2) + '秒';
        document.getElementById('result-accuracy').textContent = 
            statistics.accuracy_percent.toFixed(1) + '%';
        document.getElementById('result-wpm').textContent = 
            statistics.wpm_correct.toFixed(1);
        document.getElementById('result-cpm').textContent = 
            statistics.cpm_correct.toFixed(1);

        document.getElementById('result-correct-count').textContent = 
            statistics.correct_count;
        document.getElementById('result-incorrect-count').textContent = 
            statistics.incorrect_count;
        document.getElementById('result-backspace-count').textContent = 
            statistics.backspace_count;
        document.getElementById('result-avg-interval').textContent = 
            statistics.avg_inter_key_interval_ms.toFixed(1) + 'ms';
        document.getElementById('result-min-interval').textContent = 
            statistics.min_inter_key_interval_ms.toFixed(1) + 'ms';
        document.getElementById('result-max-interval').textContent = 
            statistics.max_inter_key_interval_ms.toFixed(1) + 'ms';

        document.getElementById('result-files').textContent = 
            `CSV ファイルが出力フォルダに保存されました\n` +
            `- ${files.events_csv}\n` +
            `- ${files.summary_csv}`;

        this.sessionId = null;
    }

    // ========== ボタンハンドラ ==========
    escapeSession() {
        if (confirm('タイピングを中止しますか？')) {
            this.finishSession();
        }
    }

    handleRetry() {
        if (this.currentScenario) {
            this.startSession(this.currentScenario);
        }
    }

    handleHome() {
        this.switchScreen('scenario-select');
        this.loadScenarios();
    }

    // ========== ユーティリティ ==========
    switchScreen(screenId) {
        // すべての画面を非表示
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.add('hidden');
            screen.classList.remove('active');
        });

        // 指定画面を表示
        const screen = document.getElementById(screenId);
        if (screen) {
            screen.classList.remove('hidden');
            screen.classList.add('active');
        }
    }
}

// ページロード時に初期化
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TypingerApp();
});
