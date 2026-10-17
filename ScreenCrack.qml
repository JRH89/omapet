import QtQuick
import Quickshell
import Quickshell.Wayland

PanelWindow {
    id: root
    required property var crack
    required property var petModel
    screen: Quickshell.screens.find(s => s.name === root.crack.screen) || Quickshell.screens[0]
    visible: petModel.pet.overlay === true
    anchors { top: true; left: true }
    margins.left: Math.round(Math.max(0, Math.min(screen.width - width, crack.x - width / 2)))
    margins.top: Math.round(Math.max(0, Math.min(screen.height - height - 36, crack.y - (height - 24) / 2)))
    implicitWidth: 160
    implicitHeight: 180
    exclusiveZone: 0
    color: "transparent"
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.namespace: "omapet-crack"
    CrackEffect {
        anchors.fill: parent
        seed: root.crack.seed
        messKind: root.crack.kind || "crack"
        onRepaired: root.petModel.run(["repair", root.crack.id])
    }
}
