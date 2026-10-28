#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="${1:-$HOME/.local/bin}"
mkdir -p "$BIN"
cat > "$BIN/spectrephish" <<EOF
#!/usr/bin/env bash
exec python3 "$ROOT/main.py" "\$@"
EOF
chmod +x "$BIN/spectrephish"
echo "[+] installed $BIN/spectrephish -> $ROOT/main.py"
case ":$PATH:" in
  *":$BIN:"*) ;;
  *) echo "[!] add to PATH:  export PATH=\"$BIN:\$PATH\"" ;;
esac
