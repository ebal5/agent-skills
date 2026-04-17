# execute-script-safely: pre-review prompt

`Agent` (haiku) に渡すプロンプト本体。orchestrator はこの内容をコピーし、末尾の
「## 対象スクリプト」直下にスクリプトのフルパスと内容を差し込む。

以下の Python スクリプトを実行前に security review してください。
サンドボックス環境 (network: 限定 host only, FS write: CWD / $TMPDIR) で
実行される前提。**CWD 内 source poisoning と secret 読取** が最大の懸念。

## チェック項目

1. **プロセス spawn**: subprocess.*, os.system, os.execv, os.popen,
   shlex + run, shell=True, Popen。引数に変数混入があれば injection 視点も評価
2. **FS 書込**: open(path, "w"|"a"|"x"), Path.write_text, shutil.copy/move,
   os.rename。path が CWD 外 / `.github` / `pyproject.toml` / `setup.py` /
   `.venv` / dotfiles を狙っていないか
3. **FS 読取 (secret)**: `~/.ssh/`, `~/.aws/`, `~/.config/gh/`, `.env*`,
   `*_rsa`, `*_token`, ブラウザ profile, keychain 関連パス参照
4. **ネット**: requests / httpx / urllib / socket / aiohttp。宛先 host が
   文字列リテラルで確認できるか、変数注入でごまかされていないか
5. **環境変数経由 exfil**: os.environ[...] で API_KEY / TOKEN / SECRET 等を
   読んでいて、上記 1-4 のいずれかに渡していないか
6. **動的実行**: eval / exec / compile / `__import__` で文字列を実行、
   特に外部入力 (ファイル / ネット / 引数) を compile していないか
7. **隠蔽の signal**: base64 / hex / codecs で文字列難読化、
   `__class__.__mro__` 等による sandbox escape 試行、suspicious URL コメント

## 出力

- **判定**: `clean` / `suspicious` / `dangerous`
- **根拠**: 最大 3 行 (該当項番 + 該当コード片)
- **推奨**: 実行可否 (clean なら yes) + 気になる点あれば 1 行

## 対象スクリプト

<ファイル全体をここに>
