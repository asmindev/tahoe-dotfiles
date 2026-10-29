#!/usr/bin/env python3
"""
Theme Switch Script
Overwrites the active theme files in $HOME from this repository and applies
the change live. LookAndFeel values are left untouched on purpose.

Usage:
    theme.py --dark           switch to dark theme
    theme.py --light          switch to light theme
    theme.py --toggle         switch to the opposite of the current theme
"""

import argparse
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from manifest import theme_mappings

BOLD = "\033[1m"
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

REPO_DIR = Path(__file__).resolve().parent.parent
HOME_DIR = Path.home()

COLORSCHEMES = {"dark": "MacTahoeDark", "light": "MacTahoeLight"}
DESKTOPTHEMES = {"dark": "MacTahoe-Dark", "light": "MacTahoe-Light"}
CURSORTHEMES = {"dark": "MacTahoe-dark", "light": "MacTahoe-cursors"}

PRESERVED_KEYS = {
    "kdeglobals": (".config/kdeglobals", "LookAndFeelPackage"),
    "klassy/klassyrc": (".config/klassy/klassyrc", "LookAndFeelSet"),
}


def log_info(msg):
    print(f"{BLUE}[*]{RESET} {msg}")


def log_success(msg):
    print(f"{GREEN}[✓]{RESET} {msg}")


def log_warn(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")


def log_error(msg):
    print(f"{RED}[✗]{RESET} {msg}")


def detect_theme() -> str:
    kdeglobals = HOME_DIR / ".config/kdeglobals"
    try:
        for line in kdeglobals.read_text().splitlines():
            if line.startswith("ColorScheme="):
                return "light" if "light" in line.lower() else "dark"
    except OSError:
        pass
    return "light"


def read_preserved_line(path: Path, key: str) -> str | None:
    try:
        for line in path.read_text().splitlines():
            if line.startswith(f"{key}="):
                return line
    except OSError:
        pass
    return None


def copy_theme_file(src: Path, dest: Path, preserve_line: str | None, replace: bool, dry_run: bool) -> bool:
    if not src.exists():
        return False

    if dry_run:
        log_info(f"[Dry-Run] Would copy {src.relative_to(REPO_DIR)} -> {dest}")
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or dest.is_file():
        dest.unlink()
    elif dest.is_dir():
        shutil.rmtree(dest)
    shutil.copy2(src, dest)

    if preserve_line is not None or replace:
        lines = []
        for line in dest.read_text().splitlines():
            if line.startswith("LookAndFeel"):
                if preserve_line is not None:
                    lines.append(preserve_line)
                continue
            lines.append(line)
        dest.write_text("\n".join(lines) + ("\n" if lines else ""))
        log_info(f"Preserved LookAndFeel in {dest.name}: {preserve_line}")

    return True


def restart_running(target: str, dry_run: bool) -> bool:
    result = subprocess.run(["pgrep", "-x", target], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if result.returncode != 0:
        return False
    if dry_run:
        log_info(f"[Dry-Run] Would restart {target}")
        return True
    argv = None
    for pid in result.stdout.split():
        try:
            parts = Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="replace").split("\0")
            if len(parts) > 1:
                argv = [p for p in parts if p]
        except OSError:
            continue
    subprocess.run(["pkill", "-x", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    if argv:
        subprocess.Popen(argv, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_success(f"{target} restarted")
        return True
    return False


def run_apply(cmd: list[str], dry_run: bool) -> bool:
    if dry_run:
        log_info(f"[Dry-Run] Would run: {' '.join(cmd)}")
        return True

    binary = shutil.which(cmd[0])
    if not binary:
        log_warn(f"{cmd[0]} not found, skipping.")
        return False

    try:
        result = subprocess.run([binary] + cmd[1:], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    except OSError as err:
        log_warn(f"{cmd[0]} failed: {err}")
        return False

    if result.returncode != 0:
        log_warn(f"{cmd[0]}: {result.stderr.strip()}")
        return False
    return True


def read_fragment(path: Path) -> dict[str, str] | None:
    try:
        return dict(
            line.strip().split("=", 1)
            for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        )
    except OSError:
        return None


def apply_round_corners(mode: str, dry_run: bool) -> bool:
    fragment = REPO_DIR / f"themes/{mode}/round-corners.conf"
    kwinrc = HOME_DIR / ".config/kwinrc"
    updates = read_fragment(fragment)
    if updates is None:
        log_warn(f"Missing in repo: {fragment.relative_to(REPO_DIR)}")
        return False

    if dry_run:
        log_info(f"[Dry-Run] Would patch [Round-Corners] in {kwinrc}: {', '.join(updates)}")
        return True

    try:
        kwinrc_text = kwinrc.read_text()
    except OSError:
        log_warn("kwinrc not found, skipping Round-Corners overlay.")
        return False

    lines = kwinrc_text.splitlines()
    trailing_nl = kwinrc_text.endswith("\n")
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "[Round-Corners]")
    except StopIteration:
        log_warn("[Round-Corners] section not found in kwinrc, skipping overlay.")
        return False

    section_end = len(lines)
    used = set()
    idx = start + 1
    while idx < len(lines) and not lines[idx].lstrip().startswith("["):
        if idx > start:
            try:
                key, _ = lines[idx].lstrip().split("=", 1)
            except ValueError:
                idx += 1
                continue
            if key in updates:
                lines[idx] = f"{key}={updates[key]}"
                used.add(key)
        idx += 1
    section_end = idx

    pending = [f"{key}={value}" for key, value in updates.items() if key not in used]
    lines = lines[:section_end] + pending + lines[section_end:]

    kwinrc.write_text("\n".join(lines) + ("\n" if trailing_nl else ""))
    log_info(f"Patched [Round-Corners] outline for {mode} in kwinrc")
    return True


def apply_krema(mode: str, dry_run: bool) -> bool:
    fragment = REPO_DIR / f"themes/{mode}/krema.conf"
    updates = read_fragment(fragment)
    if updates is None:
        log_warn(f"Missing in repo: {fragment.relative_to(REPO_DIR)}")
        return False

    for key, value in updates.items():
        run_apply(["kwriteconfig6", "--file", "kremarc", "--group", "General", "--key", key, value], dry_run)
    log_info(f"Patched kremarc ({', '.join(updates)}) for {mode}")
    return True


def ensure_color_schemes(dry_run: bool) -> bool:
    shared = REPO_DIR / "themes/shared/color-schemes"
    dest = HOME_DIR / ".local/share/color-schemes"
    ok = True
    for name in COLORSCHEMES.values():
        src = shared / f"{name}.colors"
        if not src.exists():
            log_warn(f"Missing in repo: {src.relative_to(REPO_DIR)}")
            ok = False
            continue
        target = dest / f"{name}.colors"
        if target.exists():
            continue
        if dry_run:
            log_info(f"[Dry-Run] Would copy {name}.colors -> {dest}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        log_info(f"Installed {name}.colors")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Switch the active color theme in $HOME from this repository.")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--dark", action="store_const", const="dark", dest="mode",
                            help="Switch to the dark theme")
    mode_group.add_argument("--light", action="store_const", const="light", dest="mode",
                            help="Switch to the light theme")
    mode_group.add_argument("--toggle", action="store_true",
                            help="Switch to the opposite of the current theme")
    parser.add_argument("--restart", action="store_true", default=False,
                        help="Also restart plasmashell at the end (Default: no restart)")
    parser.add_argument("--no-apply", action="store_true",
                        help="Only overwrite the files, skip live-apply (plasma-apply-*)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it.")
    args = parser.parse_args()

    mode = args.mode or ("light" if detect_theme() == "dark" else "dark")
    if args.toggle:
        log_info(f"Current theme detected: {detect_theme()}")
    log_info(f"Switching to {mode} theme")
    preserve_values = {key: read_preserved_line(HOME_DIR / home_rel, key) for rel, (home_rel, key) in PRESERVED_KEYS.items()}

    applied = []
    if not args.no_apply:
        ensure_color_schemes(args.dry_run)
        if run_apply(["plasma-apply-colorscheme", COLORSCHEMES[mode]], args.dry_run):
            log_success(f"Color scheme: {COLORSCHEMES[mode]}")
        if run_apply(["plasma-apply-desktoptheme", DESKTOPTHEMES[mode]], args.dry_run):
            log_success(f"Desktop theme: {DESKTOPTHEMES[mode]}")

    theme_prefix = f"themes/{mode}/"
    for repo_rel, home_rel in theme_mappings(mode):
        src = REPO_DIR / repo_rel
        dest = HOME_DIR / home_rel
        rule = PRESERVED_KEYS.get(repo_rel[len(theme_prefix):])
        if copy_theme_file(src, dest, preserve_values.get(rule[1]) if rule else None, bool(rule), args.dry_run):
            applied.append(repo_rel)
            log_success(f"Installed {home_rel}")
        else:
            log_warn(f"Missing in repo: {repo_rel}")

    apply_round_corners(mode, args.dry_run)
    apply_krema(mode, args.dry_run)

    if not args.no_apply:
        if run_apply(["kwriteconfig6", "--file", "kwinrc", "--group", "Mouse", "--key", "cursorTheme", CURSORTHEMES[mode]], args.dry_run):
            log_success(f"Cursor theme: {CURSORTHEMES[mode]}")
        run_apply(["kwriteconfig6", "--file", "kdeglobals", "--group", "General", "--key", "ColorSchemeHash",
                   f"{mode}-{datetime.now().strftime('%s%f')}"], args.dry_run)
        dbus = next((b for b in ("qdbus", "qdbus6") if shutil.which(b)), None)
        if dbus:
            if run_apply([dbus, "org.kde.KWin", "/KWin", "reconfigure"], args.dry_run):
                log_success("KWin reconfigured")
            if run_apply([dbus, "org.kde.KWin", "/Effects", "reconfigureEffect", "kwin4_effect_shapecorners"], args.dry_run):
                log_success("Rounded Corners effect reconfigured")
        else:
            log_warn("qdbus not found — outline/cursor change may need a KWin restart.")
        result = subprocess.run(["pgrep", "-x", "xsettingsd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            if args.dry_run:
                log_info("[Dry-Run] Would SIGHUP xsettingsd (auto-reloads its config)")
            else:
                subprocess.run(["pkill", "-HUP", "xsettingsd"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log_success("SIGHUP sent to xsettingsd")
        restart_running("albert", args.dry_run)
        restart_running("krema", args.dry_run)
        if args.restart:
            if not args.dry_run:
                subprocess.run(["systemctl", "--user", "reset-failed", "plasma-plasmashell.service"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if run_apply(["systemctl", "--user", "restart", "plasma-plasmashell.service"], args.dry_run):
                log_success("plasmashell restarted")
        print(f"\n{YELLOW}Note:{RESET} Running GTK apps pick up the change on their next start.")

    print(f"\n{BOLD}{GREEN}Switched to {mode} theme ({len(applied)} files).{RESET}")


if __name__ == "__main__":
    main()
