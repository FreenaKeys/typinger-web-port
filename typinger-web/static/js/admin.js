// admin.js - Typinger 管理画面

class AdminDashboard {
    constructor() {
        this.currentFile = null;
        this.fileList = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
    }

    // ========== イベントリスナー設定 ==========
    setupEventListeners() {
        // ナビゲーションボタン
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchSection(e.target.dataset.section));
        });

        // ダッシュボード
        document.getElementById('btn-refresh-dashboard').addEventListener('click', () => this.loadDashboard());
        document.getElementById('btn-clear-old-logs').addEventListener('click', () => this.clearOldLogs());
        document.getElementById('btn-export-all').addEventListener('click', () => this.exportAll());

        // ファイル一覧
        document.getElementById('file-type-filter').addEventListener('change', () => this.filterFiles());

        // ログビューア
        document.getElementById('btn-load-file').addEventListener('click', () => this.loadSelectedFile());
        document.getElementById('file-select').addEventListener('change', (e) => this.updateFileSelect(e));
    }

    // ========== セクション切り替え ==========
    switchSection(section) {
        if (section === 'home') {
            window.location.href = '/';
            return;
        }

        // ナビゲーションボタンを更新
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // セクションを表示
        document.querySelectorAll('.admin-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`section-${section}`).classList.add('active');

        // セクションに応じたデータ読み込み
        if (section === 'files') {
            this.loadFileList();
        } else if (section === 'viewer') {
            this.loadFileSelectOptions();
        } else if (section === 'statistics') {
            this.loadStatistics();
        }
    }

    // ========== ダッシュボード ==========
    async loadDashboard() {
        try {
            const response = await fetch('/api/admin/summary');
            const data = await response.json();

            if (data.ok) {
                this.displayDashboard(data.summary);
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    displayDashboard(summary) {
        // 統計カードを更新
        document.getElementById('stat-total-files').textContent = summary.total_csv_files;
        document.getElementById('stat-events-files').textContent = summary.file_types.events;
        document.getElementById('stat-summary-files').textContent = summary.file_types.summary;
        document.getElementById('stat-total-size').textContent = this.formatFileSize(summary.total_size_bytes);

        // 最新セッション情報を表示
        if (summary.latest_summary) {
            const latest = summary.latest_summary;
            const metrics = latest.metrics;
            
            let html = `<div class="info-item"><strong>ファイル:</strong> ${latest.filename}</div>`;
            
            if (metrics['Target Text']) {
                html += `<div class="info-item"><strong>テキスト:</strong> ${metrics['Target Text']}</div>`;
            }
            if (metrics['Total Duration (seconds)']) {
                html += `<div class="info-item"><strong>所要時間:</strong> ${metrics['Total Duration (seconds)']}秒</div>`;
            }
            if (metrics['Accuracy (%)']) {
                html += `<div class="info-item"><strong>正解率:</strong> ${metrics['Accuracy (%)']}</div>`;
            }
            if (metrics['WPM (Correct)']) {
                html += `<div class="info-item"><strong>WPM:</strong> ${metrics['WPM (Correct)']}</div>`;
            }
            
            document.getElementById('latest-session-info').innerHTML = html;
        } else {
            document.getElementById('latest-session-info').innerHTML = '<p>セッションデータがありません</p>';
        }
    }

    // ========== ファイル一覧 ==========
    async loadFileList() {
        try {
            const response = await fetch('/api/admin/csv-files');
            const data = await response.json();

            if (data.ok) {
                this.fileList = data.files;
                this.displayFileList(this.fileList);
            }
        } catch (error) {
            console.error('Error loading file list:', error);
        }
    }

    displayFileList(files) {
        const tbody = document.getElementById('files-tbody');
        tbody.innerHTML = '';

        if (files.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">ファイルがありません</td></tr>';
            return;
        }

        files.forEach(file => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${file.filename}</td>
                <td><span class="file-type-badge ${file.file_type}">${file.file_type}</span></td>
                <td>${this.formatFileSize(file.size)}</td>
                <td>${new Date(file.created_time).toLocaleString('ja-JP')}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-small btn-view" onclick="adminDashboard.viewFile('${file.filename}')">表示</button>
                        <button class="btn-small btn-download" onclick="window.open('/download/${file.filename}')">DL</button>
                        <button class="btn-small btn-delete" onclick="adminDashboard.deleteFile('${file.filename}')">削除</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    filterFiles() {
        const filter = document.getElementById('file-type-filter').value;
        
        if (filter === 'all') {
            this.displayFileList(this.fileList);
        } else {
            const filtered = this.fileList.filter(f => f.file_type === filter);
            this.displayFileList(filtered);
        }
    }

    // ========== ログビューア ==========
    async loadFileSelectOptions() {
        try {
            const response = await fetch('/api/admin/csv-files');
            const data = await response.json();

            if (data.ok) {
                const select = document.getElementById('file-select');
                select.innerHTML = '<option value="">-- ファイルを選択してください --</option>';

                data.files.forEach(file => {
                    const option = document.createElement('option');
                    option.value = file.filename;
                    option.textContent = `${file.filename} (${this.formatFileSize(file.size)})`;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading file options:', error);
        }
    }

    updateFileSelect(e) {
        // 選択されたファイル名を保存
        this.currentFile = e.target.value;
    }

    async loadSelectedFile() {
        if (!this.currentFile) {
            alert('ファイルを選択してください');
            return;
        }

        try {
            const response = await fetch(`/api/admin/csv-files/${this.currentFile}`);
            const data = await response.json();

            if (data.ok) {
                this.displayViewerContent(data.data);
            } else {
                alert('ファイルの読み込みに失敗しました');
            }
        } catch (error) {
            console.error('Error loading file:', error);
            alert('エラーが発生しました');
        }
    }

    displayViewerContent(fileData) {
        document.getElementById('viewer-content').style.display = 'block';

        // テーブルヘッダーを設定
        const thead = document.getElementById('viewer-thead');
        thead.innerHTML = `<tr>${fileData.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;

        // テーブルボディを設定
        const tbody = document.getElementById('viewer-tbody');
        tbody.innerHTML = fileData.rows.map(row => 
            `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`
        ).join('');

        // 統計情報を表示
        document.getElementById('row-count').textContent = `行数: ${fileData.row_count}`;
        document.getElementById('col-count').textContent = `列数: ${fileData.column_count}`;
    }

    viewFile(filename) {
        document.getElementById('file-select').value = filename;
        this.currentFile = filename;
        this.loadSelectedFile();
        this.switchSection('viewer');
    }

    // ========== 統計 ==========
    async loadStatistics() {
        try {
            const response = await fetch('/api/admin/export-summary');
            const data = await response.json();

            if (data.ok) {
                this.displayStatistics(data.data);
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    displayStatistics(statsData) {
        let html = `
            <div class="stats-overview">
                <div class="stat-item">
                    <span class="label">総セッション数:</span>
                    <span class="value">${statsData.total_sessions}</span>
                </div>
            </div>
            <div class="sessions-list">
        `;

        // セッションを逆順（最新から）でリスト化
        const sessions = Object.entries(statsData.sessions)
            .sort(([a], [b]) => b.localeCompare(a))
            .slice(0, 10);  // 最新10件

        sessions.forEach(([timestamp, session]) => {
            html += `
                <div class="session-item">
                    <h4>${timestamp}</h4>
                    <table class="session-metrics">
                        <tr>
                            <td>ファイル:</td>
                            <td>${session.filename}</td>
                        </tr>
            `;

            // メトリクスを表示
            for (const [key, value] of Object.entries(session.metrics).slice(0, 5)) {
                html += `<tr><td>${key}:</td><td>${value}</td></tr>`;
            }

            html += `</table></div>`;
        });

        html += `</div>`;

        document.getElementById('statistics-content').innerHTML = html;
    }

    // ========== ファイル操作 ==========
    async deleteFile(filename) {
        if (!confirm(`ファイル "${filename}" を削除してもよろしいですか？`)) {
            return;
        }

        try {
            const response = await fetch(`/api/admin/csv-files/${filename}`, {
                method: 'DELETE',
            });
            const data = await response.json();

            if (data.ok) {
                alert('ファイルを削除しました');
                this.loadFileList();
            } else {
                alert('削除に失敗しました: ' + data.error);
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            alert('エラーが発生しました');
        }
    }

    clearOldLogs() {
        alert('この機能はまだ実装されていません');
        // TODO: 実装
    }

    exportAll() {
        alert('すべてのデータをエクスポートします');
        // TODO: ZIP形式でエクスポート
    }

    // ========== ユーティリティ ==========
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// ページロード時に初期化
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});
