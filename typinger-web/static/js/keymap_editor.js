class KeymapEditor {
    constructor() {
        this.currentKeymap = { version: 1, keys: [] };
        this.selectedKeyIndex = null;
        this.keysInfo = {};
        this.init();
    }

    async init() {
        // HIDキー情報を取得
        try {
            const response = await fetch('/api/keymap/keys-info');
            const data = await response.json();
            this.keysInfo = data.keys;
        } catch (error) {
            this.showMessage('キー情報の読み込みに失敗しました', 'error');
        }

        // イベントリスナーを設定
        this.setupEventListeners();

        // 保存済みキーマップリストを更新
        await this.loadKeymapsList();

        // デフォルトキーマップを読み込み
        await this.loadDefaultKeymap();
    }

    setupEventListeners() {
        // 新規作成
        document.getElementById('btn-new').addEventListener('click', () => this.newKeymap());

        // 読み込み
        document.getElementById('btn-load').addEventListener('click', () => this.loadKeymapUI());

        // 保存
        document.getElementById('btn-save').addEventListener('click', () => this.saveKeymap());

        // リセット
        document.getElementById('btn-reset').addEventListener('click', () => this.resetKeymap());

        // ダウンロード
        document.getElementById('btn-download').addEventListener('click', () => this.downloadKeymap());

        // エクスポート
        document.getElementById('btn-export').addEventListener('click', () => this.exportKeymap());

        // プリセット選択
        document.getElementById('preset-select').addEventListener('change', (e) => {
            const value = e.target.value;
            if (value === 'load-default') {
                this.loadDefaultKeymap();
            } else if (value === 'load-dvorak') {
                this.loadDvorakKeymap();
            } else if (value === 'load-colemak') {
                this.loadColemakKeymap();
            }
            e.target.value = '';
        });

        // キーマップ名入力
        document.getElementById('keymap-name').addEventListener('change', (e) => {
            document.getElementById('keymap-name').value = e.target.value || 'custom_keymap';
        });

        // JSON インポート
        document.getElementById('btn-import-json').addEventListener('click', () => this.importJSON());

        // JSON コピー
        document.getElementById('btn-copy-json').addEventListener('click', () => {
            this.copyToClipboard('json-export');
        });

        // バイナリ コピー
        document.getElementById('btn-copy-binary').addEventListener('click', () => {
            this.copyToClipboard('binary-export');
        });

        // キー編集パネル
        document.getElementById('btn-apply').addEventListener('click', () => this.applyKeyEdit());
        document.getElementById('btn-clear-key').addEventListener('click', () => this.clearKeyEdit());

        // 修飾キーチェックボックス
        document.querySelectorAll('.mod-checkbox input').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateModValue());
        });

        // HID コード入力
        document.getElementById('edit-key-code').addEventListener('input', (e) => {
            this.updateCodeName(parseInt(e.target.value) || 0);
        });

        // 検索
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.searchKeys(e.target.value);
        });

        // ファイルアップロード
        document.getElementById('file-upload').addEventListener('change', (e) => {
            this.handleFileUpload(e);
        });
    }

    async loadDefaultKeymap() {
        try {
            const response = await fetch('/api/keymap/default');
            const keymap = await response.json();
            this.currentKeymap = keymap;
            this.renderKeyGrid();
            this.updateExports();
            this.updateInfo();
            this.showMessage('デフォルトキーマップ（QWERTY）を読み込みました', 'success');
        } catch (error) {
            this.showMessage('デフォルトキーマップの読み込みに失敗しました', 'error');
        }
    }

    loadDvorakKeymap() {
        // Dvorak配置は別途実装
        this.showMessage('Dvorakキーマップはまだ実装されていません', 'info');
    }

    loadColemakKeymap() {
        // Colemak配置は別途実装
        this.showMessage('Colemakキーマップはまだ実装されていません', 'info');
    }

    newKeymap() {
        this.currentKeymap = { version: 1, keys: [] };
        document.getElementById('keymap-name').value = 'new_keymap';
        this.renderKeyGrid();
        this.updateExports();
        this.updateInfo();
        this.showMessage('新しいキーマップを作成しました', 'success');
    }

    async loadKeymapUI() {
        const filename = prompt('キーマップのファイル名を入力してください（拡張子なし）:');
        if (!filename) return;

        try {
            const response = await fetch(`/api/keymap/${filename}.json`);
            if (!response.ok) {
                throw new Error('キーマップが見つかりません');
            }
            const data = await response.json();
            this.currentKeymap = data.keymap;
            document.getElementById('keymap-name').value = filename;
            this.renderKeyGrid();
            this.updateExports();
            this.updateInfo();
            this.showMessage(`キーマップ '${filename}' を読み込みました`, 'success');
        } catch (error) {
            this.showMessage(`読み込みエラー: ${error.message}`, 'error');
        }
    }

    async saveKeymap() {
        const filename = document.getElementById('keymap-name').value || 'custom_keymap';

        try {
            const response = await fetch('/api/keymap/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: filename + '.json',
                    keymap: this.currentKeymap
                })
            });

            const data = await response.json();
            if (response.ok) {
                this.showMessage(`キーマップ '${filename}' を保存しました`, 'success');
                await this.loadKeymapsList();
            } else {
                this.showMessage(`保存エラー: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`保存失敗: ${error.message}`, 'error');
        }
    }

    resetKeymap() {
        if (confirm('本当にリセットしますか？')) {
            this.newKeymap();
        }
    }

    downloadKeymap() {
        const filename = document.getElementById('keymap-name').value || 'custom_keymap';
        const format = document.getElementById('format-select').value;
        const url = `/api/keymap/${filename}.json/download?format=${format}`;
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.${format === 'json' ? 'json' : format === 'binary' ? 'hex' : 'b64'}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        this.showMessage('ダウンロードを開始しました', 'success');
    }

    exportKeymap() {
        const format = document.getElementById('format-select').value;
        const textareaId = format === 'json' ? 'json-export' : 'binary-export';
        const textarea = document.getElementById(textareaId);

        if (format === 'json') {
            textarea.value = JSON.stringify(this.currentKeymap, null, 2);
        } else {
            this.updateBinaryExport();
        }

        textarea.style.display = 'block';
        this.showMessage('エクスポートが完了しました', 'success');
    }

    async importJSON() {
        const jsonText = document.getElementById('json-import').value.trim();
        if (!jsonText) {
            this.showMessage('JSONが入力されていません', 'warning');
            return;
        }

        try {
            const keymap = JSON.parse(jsonText);

            // バリデーション
            const response = await fetch('/api/keymap/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(keymap)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error);
            }

            this.currentKeymap = keymap;
            this.renderKeyGrid();
            this.updateExports();
            this.updateInfo();
            document.getElementById('json-import').value = '';
            this.showMessage('JSONをインポートしました', 'success');
        } catch (error) {
            this.showMessage(`インポートエラー: ${error.message}`, 'error');
        }
    }

    renderKeyGrid() {
        const grid = document.getElementById('key-grid');
        grid.innerHTML = '';

        if (!this.currentKeymap.keys || this.currentKeymap.keys.length === 0) {
            grid.innerHTML = '<p>キーが設定されていません</p>';
            return;
        }

        this.currentKeymap.keys.forEach((key, index) => {
            const keyElement = document.createElement('button');
            keyElement.className = 'key-button';
            keyElement.textContent = key.label || this.getKeyName(key.code) || `${key.code}`;

            if (key.mods > 0) {
                keyElement.classList.add('has-modifier');
            }

            keyElement.addEventListener('click', () => {
                this.selectKey(index, key);
            });

            grid.appendChild(keyElement);
        });
    }

    selectKey(index, key) {
        this.selectedKeyIndex = index;
        document.getElementById('edit-key-label').value = key.label || '';
        document.getElementById('edit-key-code').value = key.code || 0;

        // 修飾キーを設定
        document.getElementById('mod-shift').checked = (key.mods & 0x01) !== 0;
        document.getElementById('mod-ctrl').checked = (key.mods & 0x02) !== 0;
        document.getElementById('mod-alt').checked = (key.mods & 0x04) !== 0;
        document.getElementById('mod-gui').checked = (key.mods & 0x08) !== 0;

        this.updateModValue();
        this.updateCodeName(key.code);

        // キーボタンのハイライト
        document.querySelectorAll('.key-button').forEach((btn, i) => {
            btn.classList.toggle('selected', i === index);
        });
    }

    applyKeyEdit() {
        if (this.selectedKeyIndex === null) {
            this.showMessage('キーが選択されていません', 'warning');
            return;
        }

        const label = document.getElementById('edit-key-label').value;
        const code = parseInt(document.getElementById('edit-key-code').value) || 0;
        const mods = parseInt(document.getElementById('mod-value').value) || 0;

        if (code < 0 || code > 255) {
            this.showMessage('コードは0〜255の範囲で入力してください', 'error');
            return;
        }

        this.currentKeymap.keys[this.selectedKeyIndex] = {
            code: code,
            mods: mods,
            label: label || undefined
        };

        this.renderKeyGrid();
        this.updateExports();
        this.updateInfo();
        this.showMessage('キーを更新しました', 'success');
    }

    clearKeyEdit() {
        if (this.selectedKeyIndex !== null) {
            this.currentKeymap.keys.splice(this.selectedKeyIndex, 1);
            this.selectedKeyIndex = null;
            document.getElementById('edit-key-label').value = '';
            document.getElementById('edit-key-code').value = '';
            this.renderKeyGrid();
            this.updateExports();
            this.updateInfo();
            this.showMessage('キーを削除しました', 'success');
        }
    }

    updateModValue() {
        let mods = 0;
        mods |= document.getElementById('mod-shift').checked ? 0x01 : 0;
        mods |= document.getElementById('mod-ctrl').checked ? 0x02 : 0;
        mods |= document.getElementById('mod-alt').checked ? 0x04 : 0;
        mods |= document.getElementById('mod-gui').checked ? 0x08 : 0;

        document.getElementById('mod-value').value = mods;
    }

    updateCodeName(code) {
        const name = this.getKeyName(code);
        document.getElementById('code-name').textContent = name ? `(${name})` : '';
    }

    getKeyName(code) {
        for (const [name, value] of Object.entries(this.keysInfo)) {
            if (value === code) {
                return name;
            }
        }
        return null;
    }

    updateExports() {
        // JSON エクスポート
        document.getElementById('json-export').value = JSON.stringify(this.currentKeymap, null, 2);

        // バイナリ エクスポート
        this.updateBinaryExport();
    }

    async updateBinaryExport() {
        try {
            const response = await fetch('/api/keymap/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    from_format: 'json',
                    to_format: 'hex',
                    content: this.currentKeymap
                })
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('binary-export').value = data.content;
            }
        } catch (error) {
            console.error('バイナリ変換エラー:', error);
        }
    }

    updateInfo() {
        document.getElementById('total-keys').textContent = this.currentKeymap.keys.length;
        document.getElementById('version').textContent = this.currentKeymap.version || 1;

        // バイナリサイズを計算（MAGIC(2) + version(1) + count(2) + entries(2 * count)）
        const binarySize = 5 + (this.currentKeymap.keys.length * 2);
        document.getElementById('file-size').textContent = `${binarySize} bytes`;
    }

    searchKeys(query) {
        const results = document.getElementById('search-results');
        if (!query) {
            results.innerHTML = '';
            return;
        }

        const queryLower = query.toLowerCase();
        const matches = Object.entries(this.keysInfo)
            .filter(([name, code]) => {
                return name.toLowerCase().includes(queryLower) || 
                       code.toString().includes(queryLower);
            })
            .slice(0, 10); // 最大10件

        results.innerHTML = matches.map(([name, code]) => {
            return `<div class="search-result-item" data-code="${code}">${name} (${code})</div>`;
        }).join('');

        document.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const code = parseInt(item.dataset.code);
                document.getElementById('edit-key-code').value = code;
                this.updateCodeName(code);
                results.innerHTML = '';
            });
        });
    }

    async loadKeymapsList() {
        try {
            const response = await fetch('/api/keymap/list');
            const data = await response.json();

            const listContainer = document.getElementById('keymaps-list');
            if (!data.keymaps || data.keymaps.length === 0) {
                listContainer.innerHTML = '<p>保存済みキーマップはありません</p>';
                return;
            }

            listContainer.innerHTML = data.keymaps.map(name => {
                return `
                    <div class="keymap-item">
                        <span class="keymap-name">${name}</span>
                        <div class="keymap-actions">
                            <button class="btn btn-small btn-secondary" onclick="editor.loadKeymapByName('${name}')">読み込み</button>
                            <button class="btn btn-small btn-danger" onclick="editor.deleteKeymap('${name}')">削除</button>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('キーマップリスト読み込みエラー:', error);
        }
    }

    async loadKeymapByName(filename) {
        try {
            const response = await fetch(`/api/keymap/${filename}`);
            if (!response.ok) {
                throw new Error('キーマップが見つかりません');
            }
            const data = await response.json();
            this.currentKeymap = data.keymap;
            document.getElementById('keymap-name').value = filename.replace('.json', '');
            this.renderKeyGrid();
            this.updateExports();
            this.updateInfo();
            this.showMessage(`キーマップ '${filename}' を読み込みました`, 'success');
        } catch (error) {
            this.showMessage(`読み込みエラー: ${error.message}`, 'error');
        }
    }

    async deleteKeymap(filename) {
        if (!confirm(`'${filename}' を削除してもよろしいですか？`)) return;

        try {
            const response = await fetch(`/api/keymap/${filename}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showMessage(`キーマップ '${filename}' を削除しました`, 'success');
                await this.loadKeymapsList();
            } else {
                const data = await response.json();
                this.showMessage(`削除エラー: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showMessage(`削除失敗: ${error.message}`, 'error');
        }
    }

    copyToClipboard(elementId) {
        const textarea = document.getElementById(elementId);
        textarea.select();
        document.execCommand('copy');
        this.showMessage('クリップボードにコピーしました', 'success');
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const content = e.target.result;
                document.getElementById('json-import').value = content;
                this.importJSON();
            } catch (error) {
                this.showMessage(`ファイル読み込みエラー: ${error.message}`, 'error');
            }
        };
        reader.readAsText(file);
    }

    showMessage(message, type = 'info') {
        const messageArea = document.getElementById('message-area');
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;
        messageElement.textContent = message;

        messageArea.innerHTML = '';
        messageArea.appendChild(messageElement);

        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }
}

// エディタを初期化
let editor;
document.addEventListener('DOMContentLoaded', () => {
    editor = new KeymapEditor();
});
