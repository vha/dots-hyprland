#!/usr/bin/env python3
"""
quick_configs.py

Creates a temporary directory populated with symlinks to predefined config files,
opens them in an editor and cleans up when the editor exits if possible.

Usage:
    quick_configs.py
    quick_configs.py --editor "code --wait"
"""

import argparse
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------
# Configuration: Add or modify entries here
# Format: (source_path, target_name_inside_tempdir)
CONFIG_FILES = [
    ("$HOME/.config/hypr/custom", "hypr_custom"),
    ("$HOME/.config/hypr/hyprland", "hypr_defaults_dont_edit"),
    ("$HOME/.config/hypr/hyprlock.conf", "hyprlock.conf"),
    ("$HOME/.config/hypr/hypridle.conf", "hypridle.conf"),
    ("$HOME/.config/hypr/hyprland.conf", "hyprland.conf"),
    ("$HOME/.config/hypr/monitors.conf", "monitors.conf"),
    ("$HOME/.config/hypr/workspaces.conf", "workspaces.conf"),
    ("$HOME/.config/fish/config.fish", "fish_config.fish"),
    ("$HOME/.bashrc", "bashrc"),
    ("$HOME/.zshrc", "zshrc"),
    ("$HOME/.bash_aliases", "bash_aliases"),
    # Add more here...
]
# ---------------------------------------------------------------------

DEFAULT_EDITOR = "code"


def expand(path: str) -> Path:
    """Expand ~ and environment variables cleanly."""
    return Path(os.path.expandvars(os.path.expanduser(path)))


def create_temp_workspace() -> Path:
    tempdir = Path(tempfile.mkdtemp(prefix="quick-configs-"))
    return tempdir


def create_symlinks(tempdir: Path):
    for src, target_name in CONFIG_FILES:
        src_path = expand(src)
        dest_path = tempdir / target_name

        if not src_path.exists():
            print(f"WARNING: file does not exist and is skipped: {src_path}", file=sys.stderr)
            continue

        dest_path.symlink_to(src_path)


def write_readme(tempdir: Path):
    with open(tempdir / "README.md", "w") as f:
        f.write("Temporary workspace created by quick_configs.py.\n")
        f.write("It contains symlinks to config files for quick editing.\n\n")
        f.write("Symlinked files:\n")
        for p in sorted(tempdir.iterdir()):
            f.write(f"- {p.name}\n")


def parse_editor_cmd(cmd: str, folder: Path):
    """
    Build the final command array for subprocess.
    If the editor command contains '%s', replace it with the folder path.
    Otherwise, append the folder path as the last argument.
    """
    parts = shlex.split(cmd)

    contains_placeholder = any("%s" in part for part in parts)

    if contains_placeholder:
        new_parts = []
        for part in parts:
            if "%s" in part:
                new_parts.append(part.replace("%s", str(folder)))
            else:
                new_parts.append(part)
        return new_parts
    else:
        return parts + [str(folder)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--editor",
        help='Editor command (e.g. "code --wait"). If not provided, defaults to VS Code when available.',
        default=None,
    )
    args = parser.parse_args()

    # Determine editor command
    editor_cmd = args.editor or DEFAULT_EDITOR or os.environ.get("EDITOR")

    tempdir = create_temp_workspace()
    print(f"Created temporary workspace: {tempdir}")

    create_symlinks(tempdir)
    write_readme(tempdir)

    # Prepare command array
    cmd = parse_editor_cmd(editor_cmd, tempdir)

    # Check if editor supports blocking behavior
    blocking = "--wait" in editor_cmd

    print(f"Launching editor: {' '.join(shlex.quote(p) for p in cmd)}")
    print("Blocking mode:", blocking)

    if blocking:
        # Editor will block → clean up afterwards
        try:
            subprocess.run(cmd, check=False)
        finally:
            import shutil
            shutil.rmtree(tempdir, ignore_errors=True)
            print(f"Workspace cleaned up: {tempdir}")
    else:
        # Non-blocking → launch and leave folder in place
        subprocess.Popen(cmd)
        print("\nEditor launched in non-blocking mode.")
        print(f"Temporary workspace preserved at:\n  {tempdir}\n")
        print(f"Remove it manually with:\n  rm -rf '{tempdir}'\n")


if __name__ == "__main__":
    main()
