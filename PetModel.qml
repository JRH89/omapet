import QtQuick
import Quickshell.Io

QtObject {
    id: root
    property var pet: ({name: "Sprout", character: "cat", level: 1, status: "loading", health: 100, food: 85, energy: 85, overlay: false})
    property string error: ""
    property string toast: ""
    property string effect: ""
    property var commandQueue: []
    property double seenAction: 0
    property bool initialSnapshot: false
    readonly property string executable: decodeURIComponent(Qt.resolvedUrl("bin/omapet").toString().replace("file://", ""))
    function refresh() { if (!reader.running) reader.running = true }
    function run(args) {
        if (writer.running) { commandQueue = commandQueue.concat([args]).slice(-8); return }
        error = ""
        writer.command = ["python3", executable].concat(args)
        writer.running = true
    }
    function runNext() {
        if (commandQueue.length) { let next = commandQueue[0]; commandQueue = commandQueue.slice(1); run(next) }
    }
    function syncGithub() { if (!githubSync.running) githubSync.running = true }
    function desktop(setting, value) { run(["desktop", setting, value]) }
    function act(action) { run(["care", action]) }
    function hide() { pet = Object.assign({}, pet, {overlay: false}); run(["overlay", "off"]) }
    function notify(text) { toast = text; toastTimer.restart() }
    property Process reader: Process {
        command: ["python3", root.executable, "status", "--json"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    let next = JSON.parse(text)
                    if (next.action_at && next.action_at !== root.seenAction) {
                        root.seenAction = next.action_at
                        if (Date.now() / 1000 - next.action_at < 8) {
                            root.effect = next.last_action
                            root.effectTimer.restart()
                            root.notify(next.message)
                        }
                    }
                    if (!root.initialSnapshot) {
                        root.initialSnapshot = true
                        root.syncGithub()
                    } else if (next.overlay === true && root.pet.overlay !== true) root.syncGithub()
                    root.pet = next
                } catch (e) { root.error = "Unable to read pet state" }
            }
        }
    }
    property Process githubSync: Process {
        command: ["python3", root.executable, "sync", "--auto"]
        onExited: root.refresh()
        stdout: StdioCollector { onStreamFinished: { if (text.trim()) root.notify(text.trim()) } }
    }
    property Process writer: Process {
        onExited: { root.refresh(); Qt.callLater(root.runNext) }
        stdout: StdioCollector { onStreamFinished: { if (text.trim()) root.notify(text.trim().split("\n").slice(1).join(" ")) } }
        stderr: StdioCollector { onStreamFinished: { if (text.trim()) { root.error = text.trim().replace("omapet: ", ""); root.notify(root.error) } } }
    }
    property Timer effectTimer: Timer { interval: 2400; onTriggered: root.effect = "" }
    property Timer toastTimer: Timer { interval: 5000; onTriggered: root.toast = "" }
    property Timer timer: Timer { interval: 1500; running: true; repeat: true; onTriggered: root.refresh() }
    Component.onCompleted: refresh()
}
