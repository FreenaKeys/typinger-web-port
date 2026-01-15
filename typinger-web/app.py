"""
app.py
Typinger Web - Flaskアプリケーション

タイピング練習Webアプリのメインアプリケーションファイルです。
"""

from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS
from datetime import datetime
import os
import sys

# Core modules
from core.romaji_converter import RomajiConverter
from core.typing_judge import TypingJudge, JudgeResult
from core.statistics import StatisticsCalculator, KeyEvent, EventType, StatisticsData
from core.csv_logger import CSVLogger
from core.scenario_manager import ScenarioManager
from core.log_viewer import LogViewer
from core.keymap_manager import KeymapManager, KeymapValidator
from core.keymap_converter import KeymapConverter

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize core components
scenario_manager = ScenarioManager("scenario")
csv_logger = CSVLogger("output")
log_viewer = LogViewer("output")
keymap_manager = KeymapManager("keymaps")
romaji_converter = RomajiConverter()

# Session storage (in-memory for now, can be replaced with database)
sessions = {}


@app.route('/')
def index():
    """ホームページ"""
    return render_template('index.html')


@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """利用可能なシナリオ一覧を取得"""
    scenarios = scenario_manager.get_available_scenarios()
    scenario_info_list = []
    
    for scenario_file in scenarios:
        info = scenario_manager.get_scenario_info(scenario_file)
        if info:
            scenario_info_list.append(info)
    
    return jsonify({
        "ok": True,
        "scenarios": scenario_info_list
    })


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """タイピング セッションを開始"""
    data = request.json
    scenario_file = data.get('scenario_file', 'scenarioexample.json')
    
    # シナリオから文を取得
    sentence_data = scenario_manager.get_first_sentence(scenario_file)
    if not sentence_data:
        return jsonify({
            "ok": False,
            "error": f"Scenario file not found: {scenario_file}"
        }), 404
    
    target_text, target_rubi = sentence_data
    
    # セッションを作成
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    sessions[session_id] = {
        'scenario_file': scenario_file,
        'target_text': target_text,
        'target_rubi': target_rubi,
        'judge': TypingJudge(target_text, target_rubi),
        'stats_calculator': StatisticsCalculator(),
        'events': [],
        'start_time': datetime.now(),
    }
    
    return jsonify({
        "ok": True,
        "session_id": session_id,
        "target_text": target_text,
        "target_rubi": target_rubi,
    })


@app.route('/typing/<scenario_file>')
def typing_page(scenario_file):
    """GETでタイピング画面に移動（JavaScriptなしオプション）"""
    # シナリオから文を取得
    sentence_data = scenario_manager.get_first_sentence(scenario_file)
    if not sentence_data:
        # エラーページをHTMLで返す
        return f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>エラー</title>
            <link rel="stylesheet" href="{url_for('static', filename='css/style.css')}">
        </head>
        <body>
            <div class="container">
                <header><h1>Typinger</h1></header>
                <main>
                    <div style="text-align: center; padding: 50px;">
                        <h2>❌ エラー</h2>
                        <p>シナリオが見つかりません: {scenario_file}</p>
                        <p><a href="/typing/" class="btn btn-primary" style="display: inline-block; margin-top: 20px;">設定に戻る</a></p>
                    </div>
                </main>
            </div>
        </body>
        </html>
        """, 404
    
    target_text, target_rubi = sentence_data
    
    # セッションを作成
    session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    sessions[session_id] = {
        'scenario_file': scenario_file,
        'target_text': target_text,
        'target_rubi': target_rubi,
        'judge': TypingJudge(target_text, target_rubi),
        'stats_calculator': StatisticsCalculator(),
        'events': [],
        'start_time': datetime.now(),
    }
    
    return render_template('typing.html', 
                          session_id=session_id,
                          target_text=target_text,
                          target_rubi=target_rubi)


@app.route('/typing/', defaults={'scenario_file': None})
@app.route('/typing')
def typing_setup(scenario_file):
    """タイピング設定ページ（シナリオ・キーマップ選択）"""
    return render_template('typing_setup.html')


@app.route('/api/session/<session_id>/progress', methods=['GET'])
def get_progress(session_id):
    """セッションの進捗を取得"""
    if session_id not in sessions:
        return jsonify({
            "ok": False,
            "error": "Session not found"
        }), 404
    
    session = sessions[session_id]
    judge = session['judge']
    progress = judge.get_progress_display()
    
    return jsonify({
        "ok": True,
        "progress": progress
    })


@app.route('/api/session/<session_id>/judge_char', methods=['POST'])
def judge_char(session_id):
    """1文字の入力を判定"""
    if session_id not in sessions:
        return jsonify({
            "ok": False,
            "error": "Session not found"
        }), 404
    
    data = request.json
    char = data.get('char', '')
    timestamp = data.get('timestamp', 0)  # ミリ秒単位
    
    if not char:
        return jsonify({
            "ok": False,
            "error": "Character required"
        }), 400
    
    session = sessions[session_id]
    judge = session['judge']
    stats_calc = session['stats_calculator']
    
    # 判定を実行
    result = judge.judge_char(char)
    
    # イベントを記録
    event = KeyEvent(
        event_type=EventType.KEY_DOWN,
        timestamp=timestamp * 1000,  # マイクロ秒に変換
        virtual_key=ord(char[0].upper()),
        character=char
    )
    stats_calc.add_event(event)
    session['events'].append(event)
    
    # 進捗を取得
    progress = judge.get_progress_display()
    
    return jsonify({
        "ok": True,
        "result": result.value,
        "progress": progress,
        "finished": judge.is_completed()
    })


@app.route('/api/session/<session_id>/backspace', methods=['POST'])
def handle_backspace(session_id):
    """Backspace を処理"""
    if session_id not in sessions:
        return jsonify({
            "ok": False,
            "error": "Session not found"
        }), 404
    
    data = request.json
    timestamp = data.get('timestamp', 0)
    
    session = sessions[session_id]
    judge = session['judge']
    stats_calc = session['stats_calculator']
    
    # 位置を戻す（簡易実装）
    if judge.current_position > 0:
        judge.current_position -= 1
    
    # イベントを記録
    event = KeyEvent(
        event_type=EventType.BACKSPACE,
        timestamp=timestamp * 1000,
        virtual_key=8,  # VK_BACK
        character='\b'
    )
    stats_calc.add_event(event)
    session['events'].append(event)
    
    progress = judge.get_progress_display()
    
    return jsonify({
        "ok": True,
        "progress": progress,
    })


@app.route('/api/session/<session_id>/complete', methods=['POST'])
def complete_session(session_id):
    """セッションを完了し、統計を計算・保存"""
    if session_id not in sessions:
        return jsonify({
            "ok": False,
            "error": "Session not found"
        }), 404
    
    session = sessions[session_id]
    judge = session['judge']
    stats_calc = session['stats_calculator']
    events = session['events']
    target_text = session['target_text']
    
    # 統計を計算
    stats_data = stats_calc.calculate_statistics(
        judge.get_correct_count(),
        len(judge.get_target_text())
    )
    
    accuracy = judge.get_accuracy()
    
    # CSV保存
    events_csv_path = csv_logger.save_events_csv(events)
    summary_csv_path = csv_logger.save_summary_csv(stats_data, target_text, accuracy)
    
    result = {
        "ok": True,
        "statistics": {
            "total_duration_ms": stats_data.total_duration / 1000,
            "correct_count": stats_data.correct_key_count,
            "incorrect_count": stats_data.incorrect_key_count,
            "backspace_count": stats_data.backspace_count,
            "accuracy_percent": accuracy * 100,
            "wpm_total": round(stats_data.wpm_total, 2),
            "wpm_correct": round(stats_data.wpm_correct, 2),
            "cpm_total": round(stats_data.cpm_total, 2),
            "cpm_correct": round(stats_data.cpm_correct, 2),
            "avg_inter_key_interval_ms": round(stats_data.avg_inter_key_interval, 2),
            "min_inter_key_interval_ms": round(stats_data.min_inter_key_interval, 2),
            "max_inter_key_interval_ms": round(stats_data.max_inter_key_interval, 2),
        },
        "files": {
            "events_csv": os.path.basename(events_csv_path),
            "summary_csv": os.path.basename(summary_csv_path),
        }
    }
    
    # セッションを削除
    del sessions[session_id]
    
    return jsonify(result)


@app.route('/api/session/<session_id>/finish', methods=['POST'])
def finish_session(session_id):
    """セッション完了（completeのエイリアス）"""
    return complete_session(session_id)


@app.route('/api/health', methods=['GET'])
def health():
    """ヘルスチェック"""
    return jsonify({
        "ok": True,
        "status": "Typinger Web is running",
    })


@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラ"""
    return jsonify({
        "ok": False,
        "error": "Not Found"
    }), 404


@app.errorhandler(500)
def server_error(error):
    """500エラーハンドラ"""
    return jsonify({
        "ok": False,
        "error": "Internal Server Error"
    }), 500


# ==================== 管理画面API ====================

@app.route('/admin')
def admin():
    """管理画面"""
    return render_template('admin.html')


@app.route('/api/admin/csv-files', methods=['GET'])
def get_csv_files():
    """CSVファイル一覧を取得"""
    csv_files = log_viewer.get_csv_files()
    
    return jsonify({
        "ok": True,
        "files": csv_files,
        "total_count": len(csv_files),
    })


@app.route('/api/admin/csv-files/<filename>', methods=['GET'])
def get_csv_file_content(filename):
    """CSVファイルの内容を取得"""
    # ファイル名の検証
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({
            "ok": False,
            "error": "Invalid filename"
        }), 400
    
    data = log_viewer.read_csv_file(filename)
    
    if data is None:
        return jsonify({
            "ok": False,
            "error": "File not found"
        }), 404
    
    return jsonify({
        "ok": True,
        "data": data,
    })


@app.route('/api/admin/summary', methods=['GET'])
def get_summary_statistics():
    """サマリー統計を取得"""
    summary = log_viewer.get_summary_statistics()
    
    return jsonify({
        "ok": True,
        "summary": summary,
    })


@app.route('/api/admin/export-summary', methods=['GET'])
def export_statistics_summary():
    """統計情報をエクスポート"""
    summary = log_viewer.export_statistics_summary()
    
    return jsonify({
        "ok": True,
        "data": summary,
    })


@app.route('/api/admin/csv-files/<filename>', methods=['DELETE'])
def delete_csv_file(filename):
    """CSVファイルを削除"""
    # ファイル名の検証
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({
            "ok": False,
            "error": "Invalid filename"
        }), 400
    
    success = log_viewer.delete_csv_file(filename)
    
    if not success:
        return jsonify({
            "ok": False,
            "error": "Failed to delete file"
        }), 400
    
    return jsonify({
        "ok": True,
        "message": f"File '{filename}' deleted successfully"
    })


@app.route('/download/<filename>', methods=['GET'])
def download_csv_file(filename):
    """CSVファイルをダウンロード"""
    from flask import send_file
    
    # ファイル名の検証
    if '..' in filename or '/' in filename or '\\' in filename:
        return "Invalid filename", 400
    
    filepath = os.path.join("output", filename)
    
    # セキュリティチェック
    if not os.path.abspath(filepath).startswith(os.path.abspath("output")):
        return "Invalid path", 400
    
    if not os.path.exists(filepath):
        return "File not found", 404
    
    try:
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    except Exception as e:
        return f"Error: {str(e)}", 500


# ==================== キーマップエディタ関連エンドポイント ====================

@app.route('/editor')
def keymap_editor():
    """キーマップエディタページを提供"""
    return render_template('keymap_editor.html')

@app.route('/api/keymap/keys-info')
def get_keys_info():
    """HIDキー情報を取得"""
    try:
        keys_info = {
            'keys': keymap_manager.validator.HID_KEYS,
            'modifiers': {
                'shift': 0x01,
                'ctrl': 0x02,
                'alt': 0x04,
                'gui': 0x08
            },
            'total_keys': len(keymap_manager.validator.HID_KEYS)
        }
        return jsonify(keys_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keymap/list')
def list_keymaps():
    """利用可能なキーマップ一覧を取得"""
    try:
        keymaps = keymap_manager.list_keymaps()
        return jsonify({
            'ok': True,
            'keymaps': keymaps,
            'count': len(keymaps)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/keymap/<filename>')
def get_keymap(filename):
    """特定のキーマップを取得"""
    try:
        keymap = keymap_manager.load_keymap(filename)
        return jsonify({
            'filename': filename,
            'keymap': keymap
        })
    except FileNotFoundError:
        return jsonify({'error': 'Keymap not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keymap/save', methods=['POST'])
def save_keymap():
    """キーマップを保存"""
    try:
        data = request.get_json()
        filename = data.get('filename', 'custom_keymap.json')
        keymap_data = data.get('keymap')
        
        # ファイル名のサニタイズ
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        if not filename.endswith('.json'):
            filename += '.json'
        
        # キーマップを保存
        keymap_manager.save_keymap(filename, keymap_data)
        
        return jsonify({
            'success': True,
            'message': f'Keymap saved: {filename}',
            'filename': filename
        })
    except ValueError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keymap/validate', methods=['POST'])
def validate_keymap():
    """キーマップのバリデーション"""
    try:
        keymap_data = request.get_json()
        keymap_manager.validator.validate_json(keymap_data)
        
        return jsonify({
            'valid': True,
            'message': 'Keymap is valid'
        })
    except ValueError as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keymap/convert', methods=['POST'])
def convert_keymap_format():
    """キーマップ形式を変換（JSON ↔ Binary ↔ Base64 ↔ Hex）"""
    try:
        data = request.get_json()
        from_format = data.get('from_format', 'json')  # json, binary, base64, hex
        to_format = data.get('to_format', 'binary')    # json, binary, base64, hex
        content = data.get('content')
        
        converter = KeymapConverter()
        
        # 元のフォーマットをJSON辞書に統一
        if from_format == 'json':
            if isinstance(content, str):
                json_data = json.loads(content)
            else:
                json_data = content
        elif from_format == 'binary':
            json_data = converter.binary_to_json(bytes.fromhex(content))
        elif from_format == 'base64':
            json_data = converter.base64_to_json(content)
        elif from_format == 'hex':
            json_data = converter.hex_to_json(content)
        else:
            return jsonify({'error': 'Unknown from_format'}), 400
        
        # 目的のフォーマットに変換
        if to_format == 'json':
            result = json_data
        elif to_format == 'binary':
            result = converter.json_to_binary(json_data).hex()
        elif to_format == 'base64':
            result = converter.json_to_base64(json_data)
        elif to_format == 'hex':
            result = converter.json_to_hex(json_data)
        else:
            return jsonify({'error': 'Unknown to_format'}), 400
        
        return jsonify({
            'success': True,
            'from_format': from_format,
            'to_format': to_format,
            'content': result if to_format != 'json' else json.dumps(result, ensure_ascii=False, indent=2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keymap/default')
def get_default_keymap():
    """デフォルトキーマップ（JIS配列）を取得"""
    try:
        default_keymap = keymap_manager.create_default_keymap()
        return jsonify(default_keymap)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keymap/presets/<preset>')
def get_keymap_preset(preset):
    """キーマッププリセットを取得"""
    try:
        if preset == 'jis':
            keymap = keymap_manager.create_jis_keymap()
        elif preset == 'ansi':
            keymap = keymap_manager.create_ansi_keymap()
        elif preset == 'dvorak':
            keymap = keymap_manager.create_dvorak_keymap()
        else:
            return jsonify({'ok': False, 'error': 'Unknown preset'}), 400
        
        return jsonify({'ok': True, 'keymap': keymap})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/keymap/<filename>', methods=['DELETE'])
def delete_keymap(filename):
    """キーマップを削除"""
    try:
        # ファイル名のサニタイズ
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        filepath = os.path.join("keymaps", filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Keymap not found'}), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Keymap deleted: {filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/keymap/<filename>/download')
def download_keymap(filename):
    """キーマップをダウンロード"""
    try:
        format_type = request.args.get('format', 'json')  # json, binary, base64, hex
        
        # ファイル名のサニタイズ
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        keymap = keymap_manager.load_keymap(filename)
        converter = KeymapConverter()
        
        if format_type == 'json':
            content = json.dumps(keymap, ensure_ascii=False, indent=2)
            mimetype = 'application/json'
            download_name = filename if filename.endswith('.json') else filename + '.json'
        elif format_type == 'binary':
            binary_data = converter.json_to_binary(keymap)
            content = binary_data.hex()
            mimetype = 'application/octet-stream'
            download_name = filename.replace('.json', '.bin')
        elif format_type == 'base64':
            content = converter.json_to_base64(keymap)
            mimetype = 'text/plain'
            download_name = filename.replace('.json', '.b64')
        elif format_type == 'hex':
            content = converter.json_to_hex(keymap)
            mimetype = 'text/plain'
            download_name = filename.replace('.json', '.hex')
        else:
            return jsonify({'error': 'Unknown format'}), 400
        
        return Response(
            content,
            mimetype=mimetype,
            headers={
                'Content-Disposition': f'attachment; filename="{download_name}"'
            }
        )
    except FileNotFoundError:
        return jsonify({'error': 'Keymap not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== シナリオライター関連エンドポイント ====================

@app.route('/scenario-writer')
def scenario_writer():
    """シナリオライターページを提供"""
    return render_template('scenario_writer.html')

@app.route('/api/scenario/new')
def get_new_scenario():
    """新しいシナリオテンプレートを取得"""
    try:
        template = scenario_manager.create_default_scenario()
        return jsonify(template)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/list')
def list_scenarios_api():
    """シナリオ一覧を取得"""
    try:
        scenarios = scenario_manager.get_available_scenarios()
        scenario_list = []
        
        for filename in scenarios:
            info = scenario_manager.get_scenario_info(filename)
            if info:
                scenario_list.append(info)
        
        return jsonify({
            'scenarios': scenario_list,
            'count': len(scenario_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/<filename>')
def get_scenario(filename):
    """シナリオを取得"""
    try:
        scenario = scenario_manager.load_scenario(filename)
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        return jsonify({
            'filename': filename,
            'scenario': scenario
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/save', methods=['POST'])
def save_scenario():
    """シナリオを保存"""
    try:
        data = request.get_json()
        filename = data.get('filename', 'new_scenario.json')
        scenario_data = data.get('scenario')
        
        if not scenario_data:
            return jsonify({'error': 'No scenario data provided'}), 400
        
        success, message = scenario_manager.save_scenario(filename, scenario_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'filename': filename.replace('.json', '')
            })
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/validate', methods=['POST'])
def validate_scenario():
    """シナリオのバリデーション"""
    try:
        scenario_data = request.get_json()
        valid, errors = scenario_manager.validate_scenario(scenario_data)
        
        return jsonify({
            'valid': valid,
            'errors': errors if errors else [],
            'message': '有効です' if valid else f'{len(errors)}個のエラーがあります'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/upload', methods=['POST'])
def upload_scenario():
    """シナリオファイルをアップロード"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'File must be a JSON file'}), 400
        
        # ファイルを読み込み
        try:
            scenario_data = json.loads(file.read().decode('utf-8'))
        except Exception as e:
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
        
        # バリデーション
        valid, errors = scenario_manager.validate_scenario(scenario_data)
        if not valid:
            return jsonify({'error': f'Validation failed: {", ".join(errors[:3])}'}), 400
        
        # 保存
        filename = file.filename
        success, message = scenario_manager.save_scenario(filename, scenario_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'filename': filename.replace('.json', '')
            })
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/<filename>', methods=['DELETE'])
def delete_scenario(filename):
    """シナリオを削除"""
    try:
        success, message = scenario_manager.delete_scenario(filename)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenario/<filename>/download')
def download_scenario(filename):
    """シナリオをダウンロード"""
    try:
        scenario = scenario_manager.load_scenario(filename)
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        filename = filename if filename.endswith('.json') else filename + '.json'
        
        return Response(
            json.dumps(scenario, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 出力ディレクトリを作成
    os.makedirs("output", exist_ok=True)
    
    # キーマップディレクトリを作成
    os.makedirs("keymaps", exist_ok=True)
    
    # シナリオディレクトリをコピー（まだない場合）
    if not os.path.exists("scenario"):
        os.makedirs("scenario", exist_ok=True)
    
    # 開発用サーバーを起動
    app.run(debug=True, host='0.0.0.0', port=5000)
