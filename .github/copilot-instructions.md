## Copilot AI Instructions — dots-hyprland

This repo is a collection of end_4's Hyprland dotfiles with a focus on Quickshell-based widgets (illogical-impulse). The work is mostly configuration and UI components written in QML and shell scripts that tie components together.

### High-level architecture

- **Compositor & UI**: Hyprland + Quickshell: widgets live under `dots/.config/quickshell/ii/modules` and are organized by families (e.g., `ii`, `waffle`, `common`).
- **Installer & tools**: `setup` is the entrypoint which sources `sdata/lib/*` and runs subcommands in `sdata/subcmd-*` (install, exp-update, exp-merge, uninstall, etc.).
- **Per-distro support & packaging**: `sdata/dist-*` contains distribution-specific packaging and notes, `sdata/lib/dist-determine.sh` determines the distro group.
- **Generated assets**: `matugen` outputs colors and other runtime-generated files into `~/.local/state/quickshell/user/generated` (see `dots/.config/matugen`).

### Key paths and files to reference

- Project settings and widgets: `dots/.config/quickshell/ii` ([dots/.config/quickshell/ii](dots/.config/quickshell/ii)).
- Quickshell modules: `dots/.config/quickshell/ii/modules/<family>` (e.g., `ii`, `waffle`, `common`).
- Hyprland integration: `dots/.config/hypr/*` (rules, keybinds, env.conf). Hyprland rules use `quickshell:*` layer/window names for behavior.
- Install scripts and helpers: `setup`, `sdata/subcmd-*`, `sdata/lib/functions.sh`, `sdata/lib/dist-determine.sh`.
- Packaging & distro helpers: `sdata/dist-*` and `sdata/uv` (virtualenv helper for python scripts).

### How to run & test changes locally (developer flow)

- Build/deploy the dotfiles: Clone repo & run `./setup install` (or `bash <(curl -s https://ii.clsty.link/get)` for installer script). See `setup` usage for subcommands.
- Quickshell live run: To run widgets from the terminal and view logs run `pkill qs; qs -c ii`. If widgets fail to load, logs are printed to the terminal.
- QML LSP for editing: Create `~/.config/quickshell/ii/.qmlls.ini` and configure VS Code's `Qt Qml` extension to use `qmlls6` for improved QML completions.
- Ensure Python env: `ILLOGICAL_IMPULSE_VIRTUAL_ENV` should be set (default: `~/.local/state/quickshell/.venv`). The installer places this into `~/.config/hypr/hyprland/env.conf` but you must include it or export manually.
- Reload/restart flows:
  - Reload Quickshell widgets: `pkill qs; qs -c ii &` (or `killall qs && qs -c ii`).
  - Reload Hyprland (if needed): `hyprctl reload` and ensure env.conf is applied.

### Patterns & code conventions for AI agents

- QML / Quickshell patterns:
  - Modules follow `family/module/` layout. `Config.qml` holds centralized options and defaults.
  - Use `Loader` for optional components and `FadeLoader` / `shown` flags for smooth animations.
  - Use `ScriptModel` for simple model-driven lists and `delegate` components like `SearchItem`.
  - Use `Quickshell.execDetached([...])` when invoking shell commands from QML.
  - Access shared values with `Config.options.*` and `Appearance.colors.*`.
  - Keep UIs lightweight: avoid expensive operations on frequently re-rendered paths.
- Shell & installer conventions:
  - Use `sdata/lib/functions.sh` helpers to install sync files and `sdata/lib/dist-determine.sh` to route per-distro package installers.
  - Use `sdata/subcmd-exp-merge` to merge a user's `~/.config/quickshell` for PRs (keeps tests valid for the user's custom config).
- Git / PR workflow specifics:
  - Avoid changing defaults unless there is a strong reason; keep feature toggles opt-in when possible (see `.github/CONTRIBUTING.md`).
  - Keep PRs small and focused; large refactors are better discussed in an issue first.

### Testing & debug shortcuts for agents

- Start quickshell with logs: `pkill qs; qs -c ii` to get stdout logs; `qs -c $qsConfig ipc call TEST_ALIVE` checks IPC responsiveness.
- If bar/widgets not showing, run `pkill qs; qs -c ii` and inspect the logs. See `.github/ISSUE_TEMPLATE/1-issue.yml` for suggested repro info (e.g., logs, steps).
- If you change python scripts, use the `sdata/uv/` instructions and `ILLOGICAL_IMPULSE_VIRTUAL_ENV` for test-run of `matugen` and other generators.

### Integration & external dependencies

- This repository expects Quickshell, Hyprland, and various utilities (slurp, grim, tesseract, wl-clipboard, brightnessctl, fuzzel, etc.). See `sdata/deps-info.md`.
- Nix or alternative packaging is supported via `sdata/dist-nix` and `home-manager` configs if the target system uses NixOS.

### Example changes and quick checks

- UI tweak: Edit a QML module in `dots/.config/quickshell/ii/modules/ii/<module>`, then run `pkill qs; qs -c ii` and look at the terminal logs for QML errors.
- Config option: Add property to `Config.qml` or `dots/.config/quickshell/ii/settings.qml` and read it from components via `Config.options.*`.
- Install step testing: `./setup install` will install or update system packages and copy dotfiles. To test file-copy only, run `./setup install-files`.

### Files to reference for automation & help

- Installer: [setup](setup), [sdata/lib/dist-determine.sh](sdata/lib/dist-determine.sh), [sdata/subcmd-install/3.files.sh](sdata/subcmd-install/3.files.sh).
- Quickshell & modules: [dots/.config/quickshell/ii/modules/](dots/.config/quickshell/ii/modules/), [dots/.config/quickshell/ii/defaults/](dots/.config/quickshell/ii/defaults/).
- Hyprland: [dots/.config/hypr/hyprland/](dots/.config/hypr/hyprland/).
- CONTRIBUTING & README: [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md), [.github/README.md](.github/README.md).

If anything in these instructions is unclear or if you'd like a different emphasis (e.g., more test examples, a focus on QML idioms, or a runbook for build failures), tell me and I'll refine the file.
