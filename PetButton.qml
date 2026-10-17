import QtQuick
import QtQuick.Controls as Controls

Rectangle {
    id: root
    property string hint: text
    property int textSize: 11
    property string text: ""
    signal clicked()
    width: 72; height: 27; radius: 8
    color: mouse.containsMouse && enabled ? "#426354" : "#293f40"
    opacity: enabled ? 1 : 0.5
    Text { anchors.centerIn: parent; text: root.text; color: "#d8f3e3"; font.pixelSize: root.textSize }
    Controls.ToolTip.visible: mouse.containsMouse
    Controls.ToolTip.text: hint
    Controls.ToolTip.delay: 450
    MouseArea { id: mouse; anchors.fill: parent; enabled: root.enabled; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.clicked() }
}
