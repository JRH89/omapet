import QtQuick

Item {
    id: root
    required property var group
    required property var snapshot
    width: group.width
    height: group.height
    Rectangle {
        visible: root.group.game === "four-square" && root.snapshot.mode === "four-square"
        x: parent.width * .25; y: parent.height * .27
        width: parent.width * .5; height: parent.height * .43
        radius: 4; color: "#183f7360"; border.color: "#9cbed1b8"; border.width: 2
        Rectangle { x: parent.width / 2; width: 1; height: parent.height; color: "#9cbed1b8" }
        Rectangle { y: parent.height / 2; width: parent.width; height: 1; color: "#9cbed1b8" }
        Repeater {
            model: 4
            Text {
                required property int index
                x: (index % 2) * parent.width / 2 + parent.width * .2
                y: Math.floor(index / 2) * parent.height / 2 + parent.height * .14
                text: index + 1; color: "#a9d5bf"; font.pixelSize: 14
            }
        }
    }
    Item {
        visible: root.snapshot.mode === "catch" || root.snapshot.mode === "four-square"
        x: root.snapshot.ball.x - 8; y: root.snapshot.ball.y - 8
        width: 16; height: 16; scale: root.snapshot.ball.scale
        Rectangle { x: -3; y: 25; width: 22; height: 5; radius: 3; color: "#44101d25" }
        Rectangle {
            anchors.fill: parent; radius: 8
            color: root.group.game === "catch" ? "#9ddbe4" : "#efb16e"
            border.color: "#f6e7ca"; border.width: 2
            Rectangle { x: parent.width / 2 - 1; width: 2; height: parent.height; color: "#875c46"; opacity: .6 }
            Rectangle { y: parent.height / 2 - 1; height: 2; width: parent.width; color: "#875c46"; opacity: .6 }
        }
    }
    Text {
        visible: root.snapshot.mode === "rally" || root.snapshot.mode === "bonk"
        x: parent.width * .2; y: 3; width: parent.width * .6
        text: root.snapshot.mode === "bonk" ? "TEAM BONK!" : "Troublemakers, assemble…"
        horizontalAlignment: Text.AlignHCenter
        color: "#f5d88c"; font.pixelSize: 12; font.bold: true
    }
}
