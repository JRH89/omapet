//@ pragma AppId org.omarchy.screensaver
//@ pragma ShellId omapet-screensaver
pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Io

ShellRoot {
    id: root
    property string character: "cat"
    property string petName: "Omapet"
    property double started: Date.now()
    settings.watchFiles: false
    Process {
        running: true
        command: ["python3", decodeURIComponent(Qt.resolvedUrl("bin/omapet").toString().replace("file://", "")), "screensaver", "snapshot"]
        stdout: StdioCollector {
            onStreamFinished: {
                try { let p = JSON.parse(text); root.character = p.character; root.petName = p.name }
                catch (e) { console.warn("Unable to load pet appearance", e) }
            }
        }
    }
    Variants {
        model: Quickshell.screens
        delegate: Component {
            FloatingWindow {
                id: window
                required property var modelData
                screen: modelData
                title: "Omapet screensaver"
                visible: true
                fullscreen: true
                color: "#10131b"
                property real petX: Math.random() * Math.max(0, width - 216)
                property real petY: Math.random() * Math.max(0, height - 220)
                property real vx: Math.random() < 0.5 ? -105 : 105
                property real vy: Math.random() < 0.5 ? -55 : 55
                property double lastFrame: Date.now()
                Item {
                    anchors.fill: parent
                    focus: true
                    Keys.onPressed: event => { event.accepted = true; Qt.quit() }
                    PetSprite {
                        id: runner
                        transform: Scale { origin.x: runner.width / 2; xScale: window.vx > 0 ? -1 : 1 }
                        x: window.petX; y: window.petY
                        width: 216; height: 189
                        character: root.character
                        mood: "happy"
                        effect: "run"
                    }
                    Text {
                        anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter; bottomMargin: 28 }
                        text: root.petName + " · Dreaming of adventures"
                        color: "#647080"; font.pixelSize: 14
                    }
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.BlankCursor
                        onPressed: Qt.quit()
                        onWheel: Qt.quit()
                        onPositionChanged: if (Date.now() - root.started > 1000) Qt.quit()
                    }
                }
                Timer {
                    interval: 32; running: true; repeat: true
                    onTriggered: {
                        let now = Date.now(), dt = Math.min(0.08, (now-window.lastFrame)/1000)
                        window.lastFrame = now
                        let maxX = Math.max(0, window.width-216), maxY = Math.max(0, window.height-230)
                        let x = window.petX + window.vx*dt, y = window.petY + window.vy*dt
                        if (x < 0 || x > maxX) window.vx *= -1
                        if (y < 0 || y > maxY) window.vy *= -1
                        window.petX = Math.max(0,Math.min(maxX,x)); window.petY = Math.max(0,Math.min(maxY,y))
                    }
                }
                Timer {
                    interval: 7000; running: true; repeat: true
                    onTriggered: { window.vx *= -1; window.vy = (Math.random()-0.5)*140 }
                }
            }
        }
    }
}
