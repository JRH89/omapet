import QtQuick
import Quickshell
import qs.Ui as Ui

Ui.BarWidget {
    id: root
    moduleName: "jrh89.omapet"
    implicitWidth: button.implicitWidth
    implicitHeight: button.implicitHeight
    PetModel { id: model }
    function open() { Quickshell.execDetached(["omarchy-launch-terminal", "python3", model.executable, "tui"]) }
    function close() {}
    function toggle() { open() }
    property bool opened: false
    Ui.WidgetButton {
        id: button
        anchors.fill: parent
        bar: root.bar
        text: model.pet.status || "loading"
        labelVisible: false
        fixedWidth: root.vertical ? root.barSize : content.implicitWidth + scaledHorizontalMargin * 2
        tooltipText: model.pet.name + " · Level " + model.pet.level + " · " + model.pet.status
            + "\nFood " + Math.round(model.pet.food || 0) + "% · Energy " + Math.round(model.pet.energy || 0)
            + "% · Clean " + Math.round(model.pet.hygiene || 0) + "%"
            + "\nLeft-click: care · Right-click: show / hide pet"
        onPressed: function(buttonCode) { if (buttonCode === Qt.RightButton) model.run(["overlay", "toggle"]); else if (buttonCode === Qt.LeftButton) root.open() }
        Row {
            id: content
            anchors.centerIn: parent
            spacing: 4
            PetSprite {
                width: 24; height: 24
                anchors.verticalCenter: parent.verticalCenter
                character: model.pet.character || "cat"
                mood: model.pet.status
                animated: false
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: button.text
                color: button.foreground
                font.family: button.fontFamily
                font.pixelSize: button.fontSize
                renderType: Text.NativeRendering
            }
        }
    }
    DesktopPet { model: model }
}
