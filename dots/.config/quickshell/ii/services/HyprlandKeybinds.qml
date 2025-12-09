pragma Singleton
pragma ComponentBehavior: Bound

import qs.modules.common
import qs.modules.common.functions
import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Hyprland

/**
 * A service that provides access to Hyprland keybinds.
 * Only loads keybinds if they are actively sourced in hyprland.conf.
 */
Singleton {
    id: root

    // Paths
    property string keybindParserPath: FileUtils.trimFileProtocol(`${Directories.scriptPath}/hyprland/get_keybinds.py`)
    property string hyprlandConfigPath: FileUtils.trimFileProtocol(`${Directories.config}/hypr/hyprland.conf`)
    property string defaultKeybindConfigPath: FileUtils.trimFileProtocol(`${Directories.config}/hypr/hyprland/keybinds.conf`)
    property string userKeybindConfigPath: FileUtils.trimFileProtocol(`${Directories.config}/hypr/custom/keybinds.conf`)

    // Data Storage
    property var defaultKeybinds: {"children": []}
    property var userKeybinds: {"children": []}
    
    // Combined Keybinds
    property var keybinds: ({
        children: [
            ...(defaultKeybinds.children ?? []),
            ...(userKeybinds.children ?? []),
        ]
    })

    // -------------------------------------------------------------------------
    // Logic: Initialization & Event Handling
    // -------------------------------------------------------------------------

    // Function to start the check chain
    function refreshKeybinds() {
        checkDefaultSource.running = true
        checkUserSource.running = true
    }

    // Run on Startup
    Component.onCompleted: refreshKeybinds()

    // Run on Hyprland Reload
    Connections {
        target: Hyprland
        function onRawEvent(event) {
            if (event.name == "configreloaded") {
                refreshKeybinds()
            }
        }
    }

    // -------------------------------------------------------------------------
    // 1. Check & Load DEFAULT Keybinds
    // -------------------------------------------------------------------------

    // Step 1: Check if the file is sourced in hyprland.conf
    Process {
        id: checkDefaultSource
        // grep regex explanation:
        // ^\s* -> Start of line, optional whitespace (ignores commented lines starting with #)
        // source\s*= -> "source" followed by "="
        // .* -> Any path characters
        // hyprland/keybinds\.conf -> The specific file we are looking for
        command: ["grep", "-E", "^\\s*source\\s*=\\s*.*hyprland/keybinds\\.conf", root.hyprlandConfigPath]
        
        // If grep finds the line (Exit Code 0), run the parser. Otherwise clear data.
        onExited: (exitCode) => {
            if (exitCode === 0) {
                getDefaultKeybinds.running = true
            } else {
                root.defaultKeybinds = {"children": []}
            }
        }
    }

    // Step 2: Parse the file (Only runs if Step 1 succeeds)
    Process {
        id: getDefaultKeybinds
        running: false // Do not run automatically
        command: [root.keybindParserPath, "--path", root.defaultKeybindConfigPath]
        
        stdout: SplitParser {
            onRead: data => {
                try {
                    root.defaultKeybinds = JSON.parse(data)
                } catch (e) {
                    console.error("[CheatsheetKeybinds] Error parsing default keybinds:", e)
                }
            }
        }
    }

    // -------------------------------------------------------------------------
    // 2. Check & Load USER Keybinds
    // -------------------------------------------------------------------------

    // Step 1: Check if the file is sourced in hyprland.conf
    Process {
        id: checkUserSource
        command: ["grep", "-E", "^\\s*source\\s*=\\s*.*custom/keybinds\\.conf", root.hyprlandConfigPath]
        
        onExited: (exitCode) => {
            if (exitCode === 0) {
                getUserKeybinds.running = true
            } else {
                root.userKeybinds = {"children": []}
            }
        }
    }

    // Step 2: Parse the file (Only runs if Step 1 succeeds)
    Process {
        id: getUserKeybinds
        running: false // Do not run automatically
        command: [root.keybindParserPath, "--path", root.userKeybindConfigPath]
        
        stdout: SplitParser {
            onRead: data => {
                try {
                    root.userKeybinds = JSON.parse(data)
                } catch (e) {
                    console.error("[CheatsheetKeybinds] Error parsing user keybinds:", e)
                }
            }
        }
    }
}