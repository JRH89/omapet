import QtQuick
import Quickshell
import Quickshell.Wayland
import "Playground.js" as Games

PanelWindow {
    id: root
    required property var pet
    required property var petModel
    required property var targetScreen
    required property var playground
    readonly property var activity: playground.pose(pet.id)
    screen: targetScreen
    visible: petModel.pet.overlay === true && pet.roaming === true
    anchors { top: true; left: true }
    implicitWidth: activity ? activity.size : 144
    implicitHeight: implicitWidth + 24
    color: "transparent"
    exclusiveZone: 0
    WlrLayershell.layer: WlrLayer.Top
    WlrLayershell.namespace: "omapet-companion"
    property real posX: 40 + Math.random() * Math.max(0, screen.width - 200)
    property real posY: 40 + Math.random() * Math.max(0, screen.height - 220)
    property real speedX: Math.random() < 0.5 ? -80 : 80
    property real speedY: Math.random() < 0.5 ? -38 : 38
    property double lastTick: Date.now()
    margins.left: Math.round(posX)
    margins.top: Math.round(posY)
    Timer {
        interval: 32; running: root.visible; repeat: true
        onTriggered: {
            let now = Date.now(), dt = Math.min(0.08, (now - root.lastTick) / 1000)
            root.lastTick = now
            if (root.activity) {
                let next = Games.approach(root.posX, root.posY, root.activity.x, root.activity.y, dt, 270)
                root.posX = next.x; root.posY = next.y
                return
            }
            let maxX = Math.max(0, root.screen.width - root.width)
            let maxY = Math.max(0, root.screen.height - root.height - 32)
            let nx = root.posX + root.speedX * dt, ny = root.posY + root.speedY * dt
            if (nx < 0 || nx > maxX) root.speedX *= -1
            if (ny < 0 || ny > maxY) root.speedY *= -1
            root.posX = Math.max(0, Math.min(maxX, nx))
            root.posY = Math.max(0, Math.min(maxY, ny))
        }
    }
    PetSprite {
        id: sprite
        anchors.horizontalCenter: parent.horizontalCenter
        width: root.width; height: root.width
        character: root.pet.character
        mood: root.pet.mood || root.pet.status
        effect: root.activity ? root.activity.effect : "run"
        animated: !root.activity
        drivenFrame: root.activity ? root.activity.frame : -1
        transform: Scale { origin.x: sprite.width / 2; xScale: (root.activity ? root.activity.faceRight : root.speedX > 0) ? -1 : 1 }
    }
    Rectangle {
        anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter }
        width: Math.min(parent.width, label.implicitWidth + 14); height: 22; radius: 8; color: "#ed17252e"
        Text { id: label; anchors.centerIn: parent; text: root.pet.name + (root.activity ? " · " + root.activity.label : " · L" + root.pet.level); color: "#d8f3e3"; font.pixelSize: 10 }
    }
    MouseArea {
        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onClicked: mouse => {
            if (mouse.button === Qt.RightButton) root.petModel.run(["pets", "switch", root.pet.id])
            else root.petModel.run(["pets", "roam", "off", "--pet", root.pet.id])
        }
    }
}
