function fish_prompt -d "Write out the prompt"
    # This shows up as USER@HOST /home/user/ >, with the directory colored
    # $USER and $hostname are set by fish, so you can just use them
    # instead of using `whoami` and `hostname`
    printf '%s@%s %s%s%s > ' $USER $hostname \
        (set_color $fish_color_cwd) (prompt_pwd) (set_color normal)
end

if status is-interactive # Commands to run in interactive sessions can go here

    # No greeting
    set fish_greeting
    # set -l editor vim
    set -Ux EDITOR $editor
    set -Ux SUDO_EDITOR $editor
    set -Ux VISUAL $editor
    set -Ux SYSTEMD_EDITOR $editor

    # Use starship
    starship init fish | source
    if test -f ~/.local/state/quickshell/user/generated/terminal/sequences.txt
        cat ~/.local/state/quickshell/user/generated/terminal/sequences.txt
    end

    # pyenv
    pyenv init - fish | source

    # Key bindings
    bind alt-backspace backward-kill-word

    # Aliases
    alias pamcan pacman
    alias ls 'eza --icons'
    alias clear "printf '\033[2J\033[3J\033[1;1H'"
    alias q 'qs -c ii'
    alias hc '$EDITOR $HOME/.config/hypr'
    alias hce '$EDITOR $HOME/.config/hypr/custom/env.conf'
    alias hcx '$EDITOR $HOME/.config/hypr/custom/execs.conf'
    alias hcg '$EDITOR $HOME/.config/hypr/custom/general.conf'
    alias hcr '$EDITOR $HOME/.config/hypr/custom/rules.conf'
    alias hck '$EDITOR $HOME/.config/hypr/custom/keybinds.conf'
    alias hcw '$EDITOR $HOME/.config/hypr/workspaces.conf'
    alias hcm '$EDITOR $HOME/.config/hypr/monitors.conf'
    alias qc '$EDITOR $HOME/.config/quickshell'
    alias iic '$EDITOR $HOME/.config/illogical-impulse/config.json'
    alias fc '$EDITOR $HOME/.config/fish/config.fish'
    alias zc '$EDITOR $HOME/.zshrc'
    alias bc '$EDITOR $HOME/.bashrc'
    alias c 'cd $HOME/.config'
end
