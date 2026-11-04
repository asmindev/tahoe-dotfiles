#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.13"
SRC_DIR="${QUICKBAR_SRC:-$HOME/.cache/quickbar-src}"
BUILD_DIR="${QUICKBAR_BUILD:-$HOME/.cache/quickbar-build}"
PATCH="$DIR/appmenu-pid-discovery.patch"

echo "==> Fetching QuickBar v$VERSION..."
if [ ! -d "$SRC_DIR/.git" ]; then
    git clone --depth 1 --branch "v$VERSION" https://github.com/kevinbudz/quickbar "$SRC_DIR"
else
    git -C "$SRC_DIR" fetch --depth 1 origin "refs/tags/v$VERSION"
    git -C "$SRC_DIR" checkout --force FETCH_HEAD
fi

echo "==> Applying appmenu PID discovery patch..."
git -C "$SRC_DIR" apply "$PATCH"

echo "==> Configuring with CMake..."
cmake -S "$SRC_DIR" -B "$BUILD_DIR" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr

echo "==> Building QuickBar..."
cmake --build "$BUILD_DIR" -j"$(nproc)"

echo "==> Installing (requires sudo)..."
sudo cmake --install "$BUILD_DIR"

echo "==> Restarting plasmashell..."
systemctl --user restart plasma-plasmashell.service

echo "==> Done! QuickBar rebuilt with VS Code global menu support."
