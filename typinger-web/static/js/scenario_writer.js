class ScenarioWriter {
    constructor() {
        this.currentScenario = null;
        this.selectedEntryId = null;
        this.init();
    }

    async init() {
        console.log('Scenario Writer initialized');
        this.setupEventListeners();
        await this.loadSavedScenarios();
        this.createNewScenario();
    }

    setupEventListeners() {
        // 新規作成
        document.getElementById('btn-new').addEventListener('click', () => this.createNewScenario());

        // 読み込み
        document.getElementById('btn-load').addEventListener('click', () => this.loadScenarioUI());

        // 保存
        document.getElementById('btn-save').addEventListener('click', () => this.saveScenario());

        // 検証
        document.getElementById('btn-validate').addEventListener('click', () => this.validateScenario());

        // アップロード
        document.getElementById('btn-upload').addEventListener('click', () => this.triggerFileUpload());

        // ダウンロード
        document.getElementById('btn-download').addEventListener('click', () => this.downloadScenario());

        // 削除
        document.getElementById('btn-delete').addEventListener('click', () => this.deleteScenario());

        // エントリ追加
        document.getElementById('btn-add-entry').addEventListener('click', () => this.addEntry());

        // エントリ編集適用
        document.getElementById('btn-apply-edit').addEventListener('click', () => this.applyEdit());

        // エントリ編集キャンセル
        document.getElementById('btn-clear-edit').addEventListener('click', () => this.clearEdit());

        // エディタ入力時のプレビュー更新
        document.getElementById('edit-text').addEventListener('input', () => this.updatePreview());
        document.getElementById('edit-rubi').addEventListener('input', () => this.updatePreview());
        document.getElementById('edit-level').addEventListener('change', () => this.updatePreview());

        // ファイル入力
        document.getElementById('file-upload').addEventListener('change', (e) => this.handleFileUpload(e));

        // シナリオ名・ID入力
        document.getElementById('scenario-name').addEventListener('change', (e) => {
            if (this.currentScenario && this.currentScenario.meta) {
                this.currentScenario.meta.name = e.target.value;
            }
        });

        document.getElementById('scenario-id').addEventListener('change', (e) => {
            if (this.currentScenario && this.currentScenario.meta) {
                this.currentScenario.meta.uniqueid = e.target.value;
            }
        });
    }

    createNewScenario() {
        const scenarioName = document.getElementById('scenario-name').value || 'New Scenario';
        this.currentScenario = {
            meta: {
                name: scenarioName,
                uniqueid: `com.typinger.custom_${Date.now()}`,
                requiredver: '0.1.0'
            },
            entries: {
                '1': {
                    text: 'テキスト',
                    rubi: 'tekisuto',
                    level: 'beginner'
                }
            }
        };

        this.updateUI();
        this.showMessage('新しいシナリオを作成しました', 'success');
    }

    async loadScenarioUI() {
        const filename = prompt('シナリオのファイル名を入力してください：');
        if (!filename) return;

        try {
            const response = await fetch(`/api/scenario/${filename}`);
            if (!response.ok) {
                throw new Error('シナリオが見つかりません');
            }

            const data = await response.json();
            this.currentScenario = data.scenario;
            this.updateUI();
            this.showMessage(`シナリオ '${filename}' を読み込みました`, 'success');
        } catch (error) {
            this.showMessage(`読み込みエラー: ${error.message}`, 'error');
        }
    }

    async saveScenario() {
        if (!this.currentScenario) {
            this.showMessage('シナリオが作成されていません', 'warning');
            return;
        }

        const name = document.getElementById('scenario-name').value || this.currentScenario.meta.name;
        const filename = name.replace(/\s+/g, '_').replace(/[^\w-]/g, '') + '.json';

        try {
            const response = await fetch('/api/scenario/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filename: filename,
                    scenario: this.currentScenario
                })
            });

            const data = await response.json();
            if (response.ok) {
                this.showMessage(`シナリオ '${filename}' を保存しました`, 'success');
                await this.loadSavedScenarios();
            } else {
                this.showMessage(`保存エラー: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`保存失敗: ${error.message}`, 'error');
        }
    }

    async validateScenario() {
        if (!this.currentScenario) {
            this.showMessage('シナリオが作成されていません', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/scenario/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.currentScenario)
            });

            const data = await response.json();
            if (data.valid) {
                this.showMessage('✓ シナリオは有効です', 'success');
                document.getElementById('info-status').textContent = '有効';
                document.getElementById('info-status').className = 'info-value status-valid';
            } else {
                const errors = data.errors.join('\n- ');
                this.showMessage(`✗ エラーがあります:\n- ${errors}`, 'error');
                document.getElementById('info-status').textContent = 'エラー';
                document.getElementById('info-status').className = 'info-value status-invalid';
            }
        } catch (error) {
            this.showMessage(`検証エラー: ${error.message}`, 'error');
        }
    }

    downloadScenario() {
        if (!this.currentScenario) {
            this.showMessage('シナリオが作成されていません', 'warning');
            return;
        }

        const name = document.getElementById('scenario-name').value || 'scenario';
        const filename = name.replace(/\s+/g, '_').replace(/[^\w-]/g, '') + '.json';

        const dataStr = JSON.stringify(this.currentScenario, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showMessage('ダウンロードを開始しました', 'success');
    }

    triggerFileUpload() {
        document.getElementById('file-upload').click();
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.json')) {
            this.showMessage('JSONファイルのみアップロード可能です', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/scenario/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                this.showMessage(`シナリオ '${file.name}' をアップロードしました`, 'success');
                await this.loadSavedScenarios();
                // リセット
                document.getElementById('file-upload').value = '';
            } else {
                this.showMessage(`アップロードエラー: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`アップロード失敗: ${error.message}`, 'error');
        }
    }

    async deleteScenario() {
        if (!this.currentScenario) {
            this.showMessage('シナリオが作成されていません', 'warning');
            return;
        }

        const name = document.getElementById('scenario-name').value || 'scenario';
        if (!confirm(`'${name}' を削除してもよろしいですか？`)) return;

        const filename = name.replace(/\s+/g, '_').replace(/[^\w-]/g, '') + '.json';

        try {
            const response = await fetch(`/api/scenario/${filename}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            if (response.ok) {
                this.showMessage(`シナリオ '${filename}' を削除しました`, 'success');
                await this.loadSavedScenarios();
                this.createNewScenario();
            } else {
                this.showMessage(`削除エラー: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`削除失敗: ${error.message}`, 'error');
        }
    }

    addEntry() {
        if (!this.currentScenario) {
            this.showMessage('シナリオが作成されていません', 'warning');
            return;
        }

        const entries = this.currentScenario.entries;
        const maxId = Math.max(...Object.keys(entries).map(Number));
        const newId = (maxId + 1).toString();

        entries[newId] = {
            text: '新しいエントリ',
            rubi: 'atarasii',
            level: 'beginner'
        };

        this.updateUI();
        this.selectEntry(newId);
        this.showMessage('エントリを追加しました', 'success');
    }

    selectEntry(id) {
        this.selectedEntryId = id;
        const entry = this.currentScenario.entries[id];

        document.getElementById('edit-text').value = entry.text || '';
        document.getElementById('edit-rubi').value = entry.rubi || '';
        document.getElementById('edit-level').value = entry.level || 'beginner';

        this.updatePreview();

        // ハイライト更新
        document.querySelectorAll('.entry-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.id === id) {
                item.classList.add('active');
            }
        });
    }

    updatePreview() {
        document.getElementById('preview-text').textContent = document.getElementById('edit-text').value || '-';
        document.getElementById('preview-rubi').textContent = document.getElementById('edit-rubi').value || '-';
        document.getElementById('preview-level').textContent = document.getElementById('edit-level').value || '-';
    }

    applyEdit() {
        if (this.selectedEntryId === null) {
            this.showMessage('エントリが選択されていません', 'warning');
            return;
        }

        const entry = this.currentScenario.entries[this.selectedEntryId];
        entry.text = document.getElementById('edit-text').value;
        entry.rubi = document.getElementById('edit-rubi').value;
        entry.level = document.getElementById('edit-level').value;

        this.renderEntries();
        this.showMessage('エントリを更新しました', 'success');
    }

    clearEdit() {
        document.getElementById('edit-text').value = '';
        document.getElementById('edit-rubi').value = '';
        document.getElementById('edit-level').value = 'beginner';
        this.updatePreview();
        this.selectedEntryId = null;
    }

    updateUI() {
        this.renderEntries();
        this.updateInfo();

        if (this.currentScenario && this.currentScenario.meta) {
            document.getElementById('scenario-name').value = this.currentScenario.meta.name || '';
            document.getElementById('scenario-id').value = this.currentScenario.meta.uniqueid || '';
        }
    }

    renderEntries() {
        const list = document.getElementById('entries-list');
        list.innerHTML = '';

        const entries = this.currentScenario.entries || {};
        Object.entries(entries).forEach(([id, entry]) => {
            const item = document.createElement('div');
            item.className = 'entry-item';
            if (this.selectedEntryId === id) {
                item.classList.add('active');
            }
            item.dataset.id = id;
            item.innerHTML = `
                <div class="entry-text">${entry.text}</div>
                <div class="entry-rubi">${entry.rubi}</div>
                <button class="entry-delete-btn" onclick="writer.deleteEntry('${id}')">削除</button>
            `;
            item.addEventListener('click', () => this.selectEntry(id));
            list.appendChild(item);
        });
    }

    deleteEntry(id) {
        if (confirm('このエントリを削除しますか？')) {
            delete this.currentScenario.entries[id];
            if (this.selectedEntryId === id) {
                this.selectedEntryId = null;
                this.clearEdit();
            }
            this.updateUI();
            this.showMessage('エントリを削除しました', 'success');
        }
    }

    updateInfo() {
        const entries = this.currentScenario.entries || {};
        document.getElementById('info-count').textContent = Object.keys(entries).length;
        document.getElementById('info-id').textContent = this.currentScenario.meta?.uniqueid || '-';
    }

    async loadSavedScenarios() {
        try {
            const response = await fetch('/api/scenario/list');
            const data = await response.json();

            const container = document.getElementById('saved-scenarios');
            if (!data.scenarios || data.scenarios.length === 0) {
                container.innerHTML = '<p>保存済みシナリオはありません</p>';
                return;
            }

            container.innerHTML = data.scenarios.map(scenario => {
                return `
                    <div class="scenario-card">
                        <h4>${scenario.title}</h4>
                        <p class="scenario-info">エントリ数: ${scenario.sentence_count}</p>
                        <p class="scenario-id">${scenario.filename}</p>
                        <div class="scenario-actions">
                            <button class="btn btn-small btn-secondary" onclick="writer.loadScenarioByName('${scenario.filename}')">読み込み</button>
                            <button class="btn btn-small btn-info" onclick="writer.downloadScenarioByName('${scenario.filename}')">DL</button>
                            <button class="btn btn-small btn-danger" onclick="writer.deleteScenarioByName('${scenario.filename}')">削除</button>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Error loading scenarios:', error);
        }
    }

    async loadScenarioByName(filename) {
        try {
            const response = await fetch(`/api/scenario/${filename}`);
            const data = await response.json();
            this.currentScenario = data.scenario;
            this.updateUI();
            this.showMessage(`シナリオ '${filename}' を読み込みました`, 'success');
        } catch (error) {
            this.showMessage(`読み込みエラー: ${error.message}`, 'error');
        }
    }

    downloadScenarioByName(filename) {
        const name = filename.replace('.json', '');
        document.getElementById('scenario-name').value = name;
        document.getElementById('scenario-id').value = this.currentScenario?.meta?.uniqueid || '';
        this.downloadScenario();
    }

    async deleteScenarioByName(filename) {
        if (!confirm(`'${filename}' を削除してもよろしいですか？`)) return;

        try {
            const response = await fetch(`/api/scenario/${filename}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showMessage(`シナリオ '${filename}' を削除しました`, 'success');
                await this.loadSavedScenarios();
            }
        } catch (error) {
            this.showMessage(`削除エラー: ${error.message}`, 'error');
        }
    }

    showMessage(message, type = 'info') {
        const area = document.getElementById('message-area');
        const msg = document.createElement('div');
        msg.className = `message message-${type}`;
        msg.textContent = message;

        area.innerHTML = '';
        area.appendChild(msg);

        setTimeout(() => msg.remove(), 5000);
    }
}

// 初期化
let writer;
document.addEventListener('DOMContentLoaded', () => {
    writer = new ScenarioWriter();
});
