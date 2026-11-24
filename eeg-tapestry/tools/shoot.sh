#!/bin/bash
# shoot.sh OUT.png '<json opts>'  -> renders web/poster.html headless at native size
set -e; B=$(cd "$(dirname "$0")/.." && pwd); OUT=$1; OPTS=${2:-'{}'}
SHELL_BIN=$(ls -d ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-*/chrome-headless-shell | head -1)
H=$(python3 -c "import json,math;o=json.loads('''$OPTS''');p=o.get('pitch',14.7);print(math.ceil(math.ceil(10800/o.get('cols',60))*p))")
W=$(python3 -c "import json;o=json.loads('''$OPTS''');print(round(o.get('cols',60)*o.get('pitch',14.7)))")
ENC=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote('''$OPTS'''))")
"$SHELL_BIN" --headless --hide-scrollbars --allow-file-access-from-files --window-size=$W,$H --screenshot="$OUT" "file://$B/web/poster.html#$ENC" >/dev/null 2>&1
echo "$OUT ${W}x${H}"
