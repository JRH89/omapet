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
        text: "♟ " + model.pet.name + " L" + model.pet.level
        tooltipText: model.pet.status + " · Food " + Math.round(model.pet.food) + " · Click to care"
        onPressed: function(buttonCode) { if (buttonCode === Qt.RightButton) model.run(["overlay", "toggle"]); else if (buttonCode === Qt.LeftButton) root.open() }
    }
    DesktopPet { model: model }
}
