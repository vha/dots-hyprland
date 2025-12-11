
import Quickshell
import Quickshell.Widgets
import Quickshell.Io
import qs.services
import qs.modules.common
import qs.modules.common.widgets
import QtQuick
import QtQuick.Layouts

Item {
    id: root
    implicitWidth: mainLayout.implicitWidth
    implicitHeight: mainLayout.implicitHeight
    
    Item {
        id: mainLayout
        width: parent.width

        FloatingActionButton {
            id: quickConfigsButton
            iconText: "settings"
            anchors {
                top: parent.top
                right: parent.right
                topMargin: 20
                rightMargin: 20
            }
            expanded: true
            buttonText: Translation.tr("Config files")

            downAction: () => {
                quickConfigs.running = true
            }

            Process {
                id: quickConfigs
                running: false
                command: [`${Directories.config}/hypr/custom/scripts/quick_configs.py`, "--editor", "code"]
            }

            StyledToolTip {
                text: Translation.tr("Opens a temporary folder with links to useful configuration files")
            }
        }
        
        GridLayout {
            // Layout.alignment: Qt.AlignHCenter
            id: entryGrid
            columns: 3
            columnSpacing: 40
            rowSpacing: 30

            ContentSection { // Illogical Impulse
                icon: "folder_managed"
                title: Translation.tr("Quickshell environment")

                RowLayout {
                    // Layout.alignment: Qt.AlignHCenter
                    spacing: 20
                    Layout.topMargin: 10
                    Layout.bottomMargin: 10
                    IconImage {
                        implicitSize: 80
                        source: Quickshell.iconPath("illogical-impulse")
                    }
                    ColumnLayout {
                        Layout.alignment: Qt.AlignVCenter
                        // spacing: 10
                        StyledText {
                            text: Translation.tr("illogical-impulse")
                            font.pixelSize: Appearance.font.pixelSize.title
                        }
                        StyledText {
                            text: "https://github.com/end-4/dots-hyprland"
                            font.pixelSize: Appearance.font.pixelSize.normal
                            textFormat: Text.MarkdownText
                            onLinkActivated: (link) => {
                                Qt.openUrlExternally(link)
                            }
                            PointingHandLinkHover {}
                        }
                    }
                }

                Flow {
                    Layout.fillWidth: true
                    spacing: 5

                    RippleButtonWithIcon {
                        materialIcon: "auto_stories"
                        mainText: Translation.tr("Documentation")
                        onClicked: {
                            Qt.openUrlExternally("https://end-4.github.io/dots-hyprland-wiki/en/ii-qs/02usage/")
                        }
                    }
                    RippleButtonWithIcon {
                        materialIcon: "adjust"
                        materialIconFill: false
                        mainText: Translation.tr("Issues")
                        onClicked: {
                            Qt.openUrlExternally("https://github.com/end-4/dots-hyprland/issues")
                        }
                    }
                    RippleButtonWithIcon {
                        materialIcon: "forum"
                        mainText: Translation.tr("Discussions")
                        onClicked: {
                            Qt.openUrlExternally("https://github.com/end-4/dots-hyprland/discussions")
                        }
                    }
                }
                
            }

            ContentSection { // Hyprland
                icon: "image"
                title: Translation.tr("Compositor & window manager")

                RowLayout {
                    id: hypr
                    spacing: 20
                    Layout.topMargin: 10
                    Layout.bottomMargin: 10
                    IconImage {
                        implicitSize: 80
                        source: `${Directories.config}/quickshell/ii/assets/icons/hyprland-symbolic.svg`
                    }
                    ColumnLayout {
                        Layout.alignment: Qt.AlignVCenter
                        // spacing: 10
                        StyledText {
                            text: Translation.tr("Hyprland")
                            font.pixelSize: Appearance.font.pixelSize.title
                        }
                        StyledText {
                            text: "https://github.com/hyprwm/Hyprland"
                            font.pixelSize: Appearance.font.pixelSize.normal
                            textFormat: Text.MarkdownText
                            onLinkActivated: (link) => {
                                Qt.openUrlExternally(link)
                            }
                            PointingHandLinkHover {}
                        }
                    }
                }

                Flow {
                    Layout.fillWidth: true
                    spacing: 5

                    RippleButtonWithIcon {
                        materialIcon: "auto_stories"
                        mainText: Translation.tr("Documentation")
                        onClicked: {
                            Qt.openUrlExternally("https://wiki.hypr.land/Configuring/")
                        }
                    }
                }
                
            }

            ContentSection { // Manjaro
                icon: "info"
                title: Translation.tr("Distro")

                RowLayout {
                    spacing: 20
                    Layout.topMargin: 10
                    Layout.bottomMargin: 10
                    IconImage {
                        implicitSize: 80
                        source: Quickshell.iconPath("manjaro")
                    }
                    ColumnLayout {
                        Layout.alignment: Qt.AlignVCenter
                        // spacing: 10
                        StyledText {
                            text: Translation.tr("Manjaro")
                            font.pixelSize: Appearance.font.pixelSize.title
                        }
                        StyledText {
                            text: "https://manjaro.org"
                            font.pixelSize: Appearance.font.pixelSize.normal
                            textFormat: Text.MarkdownText
                            onLinkActivated: (link) => {
                                Qt.openUrlExternally(link)
                            }
                            PointingHandLinkHover {}
                        }
                    }
                }

                Flow {
                    Layout.fillWidth: true
                    spacing: 5

                    RippleButtonWithIcon {
                        materialIcon: "auto_stories"
                        mainText: Translation.tr("Latest releases")
                        onClicked: {
                            Qt.openUrlExternally("https://forum.manjaro.org/c/announcements/11")
                        }
                    }
                }
                
            
                    
                
                
            }
        }

        Item {
            id: gap
            implicitHeight: 20
        }
    }
    
}