pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Wayland

Item {
    id: root
    required property var model
    readonly property string roamHint: model.pet.can_roam === true ? "Let out · click your pet outside to bring it home" : (model.pet.roam_block_reason || "Checking whether your pet is ready…")
    readonly property bool detailed: model.pet.desktop_view === "detailed"
    readonly property bool roaming: model.pet.roaming === true && model.pet.can_roam === true
    property bool dragging: false
    property var dragPosition: null
    readonly property var position: dragPosition || model.pet.desktop_position || null
    readonly property var selectedScreen: Quickshell.screens.find(s => root.position && s.name === root.position.screen) || Quickshell.screens[0]
    function moveBy(dx, dy) {
        if (roaming) return
        dragPosition = {
            x: Math.round(Math.max(0, Math.min(habitat.screen.width - habitat.width, habitat.margins.left + dx))),
            y: Math.round(Math.max(0, Math.min(habitat.screen.height - habitat.height - 32, habitat.margins.top + dy))),
            screen: habitat.screen.name
        }
    }
    function savePosition() {
        if (dragPosition) model.run(["position", String(dragPosition.x), String(dragPosition.y), "--screen", dragPosition.screen])
    }
    Connections {
        target: root.model
        function onPetChanged() {
            let saved = root.model.pet.desktop_position, pending = root.dragPosition
            if (!root.dragging && saved && pending && saved.x === pending.x && saved.y === pending.y && saved.screen === pending.screen)
                root.dragPosition = null
        }
    }
    property real roamX: 100
    property real roamY: 100
    property real velocityX: 88
    property real velocityY: 36
    property double lastTick: 0
    property double nextEscape: Date.now() + 15 * 60 * 1000
    function release() { model.desktop("roam", "on") }
    function home() { model.desktop("roam", "off"); nextEscape = Date.now() + 15 * 60 * 1000 }
    onRoamingChanged: {
        if (roaming) {
            roamX = habitat.margins.left
            roamY = habitat.margins.top
            velocityX = -88; velocityY = -36
            lastTick = Date.now()
            model.notify("Freedom! Click me to bring me home.")
        }
    }
    Timer {
        interval: 32; running: root.roaming && root.model.pet.overlay === true; repeat: true
        onTriggered: {
            let now = Date.now(), dt = Math.min(0.08, Math.max(0, now - root.lastTick) / 1000)
            root.lastTick = now
            let maxX = Math.max(0, habitat.screen.width - habitat.width - 8)
            let maxY = Math.max(0, habitat.screen.height - habitat.height - 48)
            let nx = root.roamX + root.velocityX * dt, ny = root.roamY + root.velocityY * dt
            if (nx < 8 || nx > maxX) root.velocityX *= -1
            if (ny < 8 || ny > maxY) root.velocityY *= -1
            root.roamX = Math.max(8, Math.min(maxX, nx))
            root.roamY = Math.max(8, Math.min(maxY, ny))
        }
    }
    Timer {
        interval: 5500; running: root.roaming; repeat: true
        onTriggered: {
            root.velocityX = (root.velocityX < 0 ? -1 : 1) * (60 + Math.random() * 70)
            root.velocityY = (Math.random() < 0.5 ? -1 : 1) * (20 + Math.random() * 35)
        }
    }
    Timer {
        interval: 60000; running: true; repeat: true
        onTriggered: {
            let p = root.model.pet
            // A 15 minute grace period, then 8% chance per minute while eligible.
            // No checks while hidden, asleep, sick, away, or already outside.
            if (!root.roaming && p.overlay && p.escapes !== false && p.can_roam && Date.now() > root.nextEscape
                && Date.now() / 1000 - (p.escape_at || 0) > 900 && Math.random() < 0.08) root.release()
        }
    }
    PanelWindow {
        id: habitat
        visible: root.model.pet.overlay === true
        screen: root.selectedScreen
        anchors { top: true; left: true }
        margins.left: Math.round(root.roaming ? root.roamX : Math.max(0, Math.min(screen.width - width, root.position ? root.position.x : screen.width - width - 24)))
        margins.top: Math.round(root.roaming ? root.roamY : Math.max(0, Math.min(screen.height - height - 32, root.position ? root.position.y : screen.height - height - 50)))
        implicitWidth: root.roaming ? 144 : root.detailed ? 276 : 218
        implicitHeight: root.roaming ? 148 : content.implicitHeight + (root.detailed ? 47 : 37)
        color: "transparent"
        exclusiveZone: 0
        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.namespace: "omapet"
        Rectangle {
            anchors.fill: parent; visible: !root.roaming
            color: "#f717252e"; radius: 18
            border.color: root.model.effect === "clean" ? "#b5eff1" : "#426354"
            PetDragArea { anchors.fill: parent; desktop: root }
            Text { x: 14; y: 12; text: root.detailed ? "O M A P E T" : root.model.pet.name + " · L" + root.model.pet.level; color: "#8fac9e"; font.pixelSize: 10 }
            Rectangle {
                anchors { top: parent.top; right: parent.right; margins: 8 }
                visible: root.detailed
                width: 30; height: 26; radius: 8; color: hideMouse.containsMouse ? "#426354" : "transparent"
                Text { anchors.centerIn: parent; text: "×"; color: "#d8f3e3"; font.pixelSize: 21 }
                MouseArea { id: hideMouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.model.hide() }
            }
            Column {
                id: content
                x: 14; y: root.detailed ? 35 : 27; width: parent.width - 28; spacing: 6
                PetSprite {
                    anchors.horizontalCenter: parent.horizontalCenter
                    implicitWidth: root.detailed ? 124 : 96; implicitHeight: root.detailed ? 100 : 76
                    mood: root.model.pet.status; character: root.model.pet.character || "cat"; effect: root.model.effect
                    PetDragArea { anchors.fill: parent; desktop: root; onTapped: root.model.act("feed") }
                }
                Text { visible: root.detailed; anchors.horizontalCenter: parent.horizontalCenter; text: root.model.pet.name + " · L" + root.model.pet.level; color: "#d8f3e3"; font.pixelSize: 15; font.bold: true }
                Text { visible: root.detailed; anchors.horizontalCenter: parent.horizontalCenter; text: root.model.pet.status; color: "#a6beb3"; font.pixelSize: 11 }
                Text {
                    visible: !root.detailed; anchors.horizontalCenter: parent.horizontalCenter
                    text: "♥ " + Math.round(root.model.pet.health) + "   ◒ " + Math.round(root.model.pet.food) + "   ϟ " + Math.round(root.model.pet.energy)
                    color: "#a6beb3"; font.pixelSize: 11
                }
                Column {
                    visible: root.detailed; width: parent.width; spacing: 5
                    Repeater {
                        model: [{key: "health", label: "Health"}, {key: "food", label: "Food"}, {key: "energy", label: "Energy"}, {key: "hygiene", label: "Clean"}, {key: "joy", label: "Joy"}]
                        delegate: Item {
                            id: statRow
                            required property var modelData
                            readonly property real value: Number(root.model.pet[modelData.key] || 0)
                            width: content.width; height: 14
                            Text { text: statRow.modelData.label; color: "#a6beb3"; font.pixelSize: 11 }
                            Rectangle {
                                x: 55; y: 4; width: parent.width - 87; height: 6; radius: 3; color: "#304449"
                                Rectangle { width: parent.width * Math.max(0, Math.min(100, statRow.value)) / 100; height: 6; radius: 3; color: statRow.value < 25 ? "#e9b47f" : "#9bd9b7"; Behavior on width { NumberAnimation { duration: 250 } } }
                            }
                            Text { anchors.right: parent.right; text: Math.round(statRow.value); color: "#d8f3e3"; font.pixelSize: 11 }
                        }
                    }
                    Rectangle { width: parent.width; height: 1; color: "#304449" }
                    Text {
                        width: parent.width; horizontalAlignment: Text.AlignHCenter
                        property var traits: root.model.pet.traits || ({})
                        text: "STR " + (traits.strength || 0) + "   STA " + (traits.stamina || 0) + "   AGI " + (traits.agility || 0) + "   DEF " + (traits.defense || 0)
                        color: "#c4b7de"; font.pixelSize: 11
                    }
                    Text {
                        width: parent.width; horizontalAlignment: Text.AlignHCenter
                        text: (root.model.pet.xp || 0) + " XP  ·  next level at " + (100 * Math.pow(root.model.pet.level || 1, 2))
                        color: "#d8f3e3"; font.pixelSize: 11
                    }
                    Text {
                        width: parent.width; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap
                        text: "GitHub: " + (root.model.pet.account || "not connected") + "\nLast activity: " + (root.model.pet.last_active || "not synced")
                        color: "#8fac9e"; font.pixelSize: 10
                    }
                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter; spacing: 6
                        PetButton { text: "Play"; onClicked: root.model.act("play") }
                        PetButton { text: "Medicine"; onClicked: root.model.act("medicine") }
                        PetButton { text: root.model.pet.vacation ? "Return" : "Vacation"; onClicked: root.model.act("vacation") }
                    }
                }
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter; spacing: 6
                    visible: root.detailed
                    PetButton { text: "Feed"; onClicked: root.model.act("feed") }
                    PetButton { text: "Clean"; onClicked: root.model.act("clean") }
                    PetButton { text: root.model.pet.sleeping ? "Wake" : "Rest"; onClicked: root.model.act(root.model.pet.sleeping ? "wake" : "sleep") }
                }
                Row {
                    anchors.horizontalCenter: parent.horizontalCenter; spacing: 6
                    visible: root.detailed
                    PetButton { width: 111; text: root.detailed ? "Simple view" : "Detailed view"; onClicked: root.model.desktop("view", "toggle") }
                    PetButton { width: 111; text: "Let out ↗"; hint: root.roamHint; available: root.model.pet.can_roam === true; onClicked: root.release() }
                }
                PetButton {
                    visible: root.detailed; width: parent.width; height: 23
                    text: "Surprise escapes: " + (root.model.pet.escapes === false ? "off" : "on")
                    onClicked: root.model.desktop("escapes", root.model.pet.escapes === false ? "on" : "off")
                }
                Row {
                    visible: !root.detailed
                    anchors.horizontalCenter: parent.horizontalCenter; spacing: 4
                    PetButton { width: 28; text: "◒"; hint: "Feed"; textSize: 16; onClicked: root.model.act("feed") }
                    PetButton { width: 28; text: "✧"; hint: "Clean"; textSize: 17; onClicked: root.model.act("clean") }
                    PetButton { width: 28; text: root.model.pet.sleeping ? "☀" : "☾"; hint: root.model.pet.sleeping ? "Wake" : "Sleep"; textSize: 16; onClicked: root.model.act(root.model.pet.sleeping ? "wake" : "sleep") }
                    PetButton { width: 28; text: "≡"; hint: "Detailed view"; textSize: 19; onClicked: root.model.desktop("view", "detailed") }
                    PetButton { width: 28; text: "↗"; hint: root.roamHint; textSize: 17; available: root.model.pet.can_roam === true; onClicked: root.release() }
                    PetButton { width: 28; text: "×"; hint: "Hide"; textSize: 19; onClicked: root.model.hide() }
                }
            }
        }
        Rectangle {
            visible: !root.roaming && root.model.toast.length > 0
            x: 8; y: 30; width: parent.width - 16; height: toastText.implicitHeight + 12; radius: 8
            color: "#f7293f40"
            Text { id: toastText; x: 6; y: 6; width: parent.width - 12; text: root.model.toast; color: root.model.error ? "#e9b47f" : "#d8f3e3"; font.pixelSize: 10; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter }
        }
        Item {
            anchors.fill: parent; visible: root.roaming
            PetSprite {
                id: runner
                anchors.horizontalCenter: parent.horizontalCenter
                mood: root.model.pet.status; character: root.model.pet.character || "cat"; effect: "run"
                transform: Scale { origin.x: runner.width / 2; xScale: root.velocityX > 0 ? -1 : 1 }
            }
            Rectangle {
                anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter }
                width: Math.min(parent.width, returnLabel.implicitWidth + 14); height: 22; radius: 8; color: "#ed17252e"
                Text { id: returnLabel; anchors.centerIn: parent; text: "Click to go home"; color: "#d8f3e3"; font.pixelSize: 10 }
            }
            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: root.home() }
        }
    }
}
