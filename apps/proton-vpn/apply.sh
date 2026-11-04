#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_PACKAGES="$(python -c 'import site; print(site.getsitepackages()[0])')"
TARGET="$SITE_PACKAGES/proton/vpn/app/gtk/widgets/headerbar/menu/menu.py"
PATCH="$DIR/dbusmenu-export.patch"

if [ ! -f "$TARGET" ]; then
    echo "Proton VPN menu.py not found at $TARGET"
    exit 1
fi

if sudo patch -d "$SITE_PACKAGES" -p1 --dry-run --reverse < "$PATCH" >/dev/null 2>&1; then
    echo "Proton VPN global menu patch is already applied."
    exit 0
fi

sudo patch -d "$SITE_PACKAGES" -p1 < "$PATCH"
echo "Applied. Restart Proton VPN for the menu to appear."
