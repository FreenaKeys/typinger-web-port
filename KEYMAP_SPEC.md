## KEYMAP 仕様書（LLM に投げられる形式）

目的
- Webタイピング、Windows用ユーティリティ、Frekeys ファームウェアで共通に使えるキーマップ仕様を定義する。

前提
- キー数: `SHIFT165_CHIPS * 8`（ビルド時に決定）
- HID コードは 0..255
- 修飾はビットフラグ（Shift, Ctrl, Alt, GUI）として扱う

スキーマ（JSON で人間可読 & 機械検証可能）

```json
{
  "version": 1,
  "keys": [
    { "code": 4, "mods": 0, "label": "A" },
    { "code": 5, "mods": 0, "label": "B" }
    // ... 合計 (expected_keys) 個
  ]
}
```

フィールド説明
- `version` : スキーマバージョン（uint8）
- `keys` : 配列。配列インデックスが物理位置を表す。
  - `code` : HID Usage ID（uint8、0=無割当）
  - `mods` : 修飾ビット（uint8、bit0=Shift, bit1=Ctrl, bit2=Alt, bit3=GUI）
  - `label` (任意): 表示用ラベル

バイナリ保存フォーマット（EEPROM / 転送用）
- リトルエンディアンで以下の順序:
  1. `uint16` MAGIC = 0xA5A5
  2. `uint8` version
  3. `uint16` count (キー数)
  4. count 個のエントリ、各エントリは `uint8 code`, `uint8 mods`

例:  (count=64 のときの長さ)
- 2 (magic) + 1 (version) + 2 (count) + 64*(1+1) = 135 bytes

検証ルール（必須）
- `keys.length == expected_keys`
- 各 `code` は 0..255
- 各 `mods` は 0..15
- magic と count を検証

LLM に投げるための最短プロンプトテンプレート

```
仕様 = <このファイルの JSON スキーマとバイナリフォーマット>
命令:
1) 入力 JSON（次のフォーマット）を検証せよ。
2) 検証 OK ならバイナリを生成して base64 で返せ。
3) 返す JSON 構造: { "ok":true, "base64":"...", "hex":"..." }
   エラー時は { "ok":false, "errors":[...] }

入力 JSON 例:
{ "version":1, "keys":[ {"code":4, "mods":0}, ... ] }
```

PC側ワークフロー（推奨）
1. ユーザは JSON を編集（ブラウザ / エディタ）
2. JSON を LLM / ツールに投げて検証
3. 検証済みバイナリを base64 で受け取り、シリアル経由で ESP に送る
4. ESP 側は受け取ったバイナリを parse して EEPROM に保存し、適用

参考: Python スニペット（JSON→バイナリ→base64）

```python
import json,base64,struct

def json_to_blob(j):
    keys = j['keys']
    count = len(keys)
    header = struct.pack('<H B H', 0xA5A5, j['version'], count)
    body = b''.join(struct.pack('BB', k['code'], k['mods']) for k in keys)
    return base64.b64encode(header+body).decode('ascii')

# 使い方:
# j = json.load(open('keymap.json'))
# print(json_to_blob(j))
```

注意
- ESP32 で JSON を直接パースするのはコストが高い。可能なら PC/ブラウザ側で変換してから転送する運用を推奨する。
- 将来フィールドを追加する際は `version` を用いた互換処理を実装すること。

---

ファイル生成者: 自動生成 (要求日時: 2026-01-14)
