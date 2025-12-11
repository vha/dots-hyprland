#!/bin/bash

# Multimonitor support for scattered workspaces switching

direction="$1"  # next | prev
CONFIG="$HOME/.config/hypr/hyprland.conf"

monitor=$(hyprctl -j monitors | jq -r '.[] | select(.focused==true) | .name')

# Extract the workspace order from your hyprland.conf
# Supports lines like:
#   workspace=1,monitor:DP-4
#   workspace=name:/,monitor:DP-4
#   workspace=chat,monitor:HDMI-A-2
mapfile -t ordered_ws < <(
    grep -E '^workspace=' "$CONFIG" \
    | sed 's/workspace=//' \
    | sed 's/,.*//' \
    | sed 's/name://g' \
    | sed 's/ //g'
)

# Current workspace (string)
current=$(
    hyprctl -j activeworkspace \
    | jq -r 'if .name != "" then .name else (.id|tostring) end'
)

# Collect ONLY workspaces with windows ON THIS MONITOR
mapfile -t active_ws < <(
    hyprctl -j workspaces \
    | jq -r --arg mon "$monitor" '
        .[]
        | select(.monitor == $mon and .windows > 0)
        | if .name != "" then .name else (.id|tostring) end
    '
)

# Build a list in CONFIG ORDER but only those active on this monitor
filtered=()
for ws in "${ordered_ws[@]}"; do
    for active in "${active_ws[@]}"; do
        if [ "$ws" = "$active" ]; then
            filtered+=("$ws")
        fi
    done
done

# Nothing active → exit
if [ ${#filtered[@]} -eq 0 ]; then
    exit 0
fi

# Find current index in filtered list
idx=-1
for i in "${!filtered[@]}"; do
    if [ "${filtered[$i]}" = "$current" ]; then
        idx=$i
        break
    fi
done

# If current isn't active (empty workspace), jump to the first active
if [ $idx -eq -1 ]; then
    hyprctl dispatch workspace "${filtered[0]}"
    exit 0
fi

# Move
if [ "$direction" = "next" ]; then
    target=$((idx + 1))
else
    target=$((idx - 1))
fi

# No wrap
if [ $target -lt 0 ] || [ $target -ge ${#filtered[@]} ]; then
    exit 0
fi

hyprctl dispatch workspace "${filtered[$target]}"

