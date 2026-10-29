"""Shared path manifest for install.py and sync.py."""

from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

# (path in repo, path in $HOME)
GLOBAL_MAPPINGS = [
    # Desktop / Plasma
    ("desktop/plasma/config/plasmashellrc", ".config/plasmashellrc"),
    ("desktop/plasma/config/plasma-org.kde.plasma.desktop-appletsrc", ".config/plasma-org.kde.plasma.desktop-appletsrc"),
    ("desktop/plasma/look-and-feel/MY LIGHT TAHOE", ".local/share/plasma/look-and-feel/MY LIGHT TAHOE"),
    ("desktop/plasma/look-and-feel/MY TAHOE DARK", ".local/share/plasma/look-and-feel/MY TAHOE DARK"),
    ("desktop/plasma/desktoptheme/MacTahoe-Light", ".local/share/plasma/desktoptheme/MacTahoe-Light"),
    ("desktop/plasma/desktoptheme/MacTahoe-Dark", ".local/share/plasma/desktoptheme/MacTahoe-Dark"),
    ("desktop/plasma/plasmoids", ".local/share/plasma/plasmoids"),
    ("desktop/kwin/config/kwinrc", ".config/kwinrc"),
    ("desktop/kwin/config/kwinrulesrc", ".config/kwinrulesrc"),
    ("desktop/kwin/scripts", ".local/share/kwin/scripts"),
    ("desktop/decorations/klassy/windecopresetsrc", ".config/klassy/windecopresetsrc"),
    ("desktop/decorations/darkly/darklyrc", ".config/darklyrc"),

    # Shared GTK assets
    ("themes/shared/gtk-3.0/bookmarks", ".config/gtk-3.0/bookmarks"),
    ("themes/shared/gtk-3.0/gtk.css", ".config/gtk-3.0/gtk.css"),
    ("themes/shared/gtk-3.0/assets", ".config/gtk-3.0/assets"),
    ("themes/shared/gtk-4.0/gtk.css", ".config/gtk-4.0/gtk.css"),
    ("themes/shared/gtk-4.0/gtk-Dark.css", ".config/gtk-4.0/gtk-Dark.css"),
    ("themes/shared/gtk-4.0/gtk-Light.css", ".config/gtk-4.0/gtk-Light.css"),
    ("themes/shared/gtk-4.0/gtk-dark.css", ".config/gtk-4.0/gtk-dark.css"),
    ("themes/shared/gtk-4.0/assets", ".config/gtk-4.0/assets"),
    ("themes/shared/gtk-4.0/windows-assets", ".config/gtk-4.0/windows-assets"),
    ("themes/shared/color-schemes", ".local/share/color-schemes"),

    # Shell
    ("shell/zsh/.zshrc", ".zshrc"),
    ("shell/zsh/.p10k.zsh", ".p10k.zsh"),
    ("shell/konsole/konsolerc", ".config/konsolerc"),
    ("shell/konsole/profiles", ".local/share/konsole"),
    ("shell/alacritty", ".config/alacritty"),
    ("shell/cava", ".config/cava"),
    ("shell/starship/starship.toml", ".config/starship.toml"),

    # Dolphin
    ("apps/dolphin/config/dolphinrc", ".config/dolphinrc"),
    ("apps/dolphin/qss/dolphin.qss", ".config/dolphin/dolphin.qss"),
    ("apps/dolphin/kxmlgui5/dolphin", ".local/share/kxmlgui5/dolphin"),
    ("apps/dolphin/kxmlgui6/dolphin", ".local/share/kxmlgui6/dolphin"),
    ("apps/dolphin/bin/dolphin", ".local/bin/dolphin"),
    ("apps/dolphin/applications/org.kde.dolphin.desktop", ".local/share/applications/org.kde.dolphin.desktop"),

    # Albert
    ("apps/albert/config", ".config/albert"),
    ("apps/albert/autostart/albert.desktop", ".config/autostart/albert.desktop"),
    ("apps/albert/share/widgetsboxmodel/themes", ".local/share/albert/widgetsboxmodel/themes"),
    ("apps/albert/applications/albert-toggle.desktop", ".local/share/applications/albert-toggle.desktop"),
]

# (path inside the active theme folder, path in $HOME)
THEME_MAPPINGS = [
    ("kdeglobals", ".config/kdeglobals"),
    ("klassy/klassyrc", ".config/klassy/klassyrc"),
    ("gtk-3.0/settings.ini", ".config/gtk-3.0/settings.ini"),
    ("gtk-3.0/colors.css", ".config/gtk-3.0/colors.css"),
    ("gtk-4.0/settings.ini", ".config/gtk-4.0/settings.ini"),
    ("gtk-4.0/colors.css", ".config/gtk-4.0/colors.css"),
    ("xsettingsd.conf", ".config/xsettingsd/xsettingsd.conf"),
    (".gtkrc-2.0", ".gtkrc-2.0"),
    ("konsole/MacTahoe.colorscheme", ".local/share/konsole/MacTahoe.colorscheme"),
]

SYNC_IGNORE = ("*.bak", "*.bak.*", "*.toml.*", "*.tbcache", "*~")


def theme_mappings(theme: str):
    """Return (repo path, home path) pairs for a given theme."""
    return [(f"themes/{theme}/{repo_rel}", home_rel) for repo_rel, home_rel in THEME_MAPPINGS]
