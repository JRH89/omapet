import QtQuick

Item {
    id: root
    property int seed: 1
    property bool fixing: false
    signal repaired()
    implicitWidth: 160
    implicitHeight: 180
    onSeedChanged: glass.requestPaint()
    Canvas {
        id: glass
        width: parent.width; height: parent.height - 24
        opacity: root.fixing ? 0 : 1
        scale: root.fixing ? 1.12 : 1
        Behavior on opacity { NumberAnimation { duration: 260 } }
        Behavior on scale { NumberAnimation { duration: 260 } }
        onPaint: {
            let c = getContext("2d"); c.reset()
            let state = root.seed % 233280
            function random() { state = (state * 9301 + 49297) % 233280; return state / 233280 }
            let cx = width / 2, cy = height / 2, rays = []
            for (let i = 0; i < 7; i++) {
                let angle = i * Math.PI * 2 / 7 + (random() - 0.5) * 0.35
                let length = 42 + random() * 28
                let points = [[cx,cy]]
                for (let n = 1; n <= 3; n++) {
                    let r = length * n / 3, offset = (random() - 0.5) * 12
                    points.push([cx + Math.cos(angle)*r - Math.sin(angle)*offset,
                                 cy + Math.sin(angle)*r + Math.cos(angle)*offset])
                }
                let fork = angle + (random() < 0.5 ? -0.7 : 0.7)
                rays.push(points)
                rays.push([points[2], [points[2][0] + Math.cos(fork)*16, points[2][1] + Math.sin(fork)*16]])
            }
            function stroke(color, lineWidth, offset) {
                c.strokeStyle = color; c.lineWidth = lineWidth; c.lineJoin = "miter"
                for (let points of rays) {
                    c.beginPath(); c.moveTo(points[0][0]+offset, points[0][1]+offset)
                    for (let n=1;n<points.length;n++) c.lineTo(points[n][0]+offset,points[n][1]+offset)
                    c.stroke()
                }
            }
            stroke("#b8202937", 3.5, 1)
            stroke("#e4edf4f5", 1.2, 0)
            c.strokeStyle="#c5f2f6f3"; c.lineWidth=1
            c.beginPath(); c.moveTo(cx-4,cy-3); c.lineTo(cx+3,cy-5); c.lineTo(cx+6,cy+2); c.lineTo(cx,cy+6); c.closePath(); c.stroke()
        }
    }
    Rectangle {
        anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter }
        width: 90; height: 23; radius: 8
        color: root.fixing ? "#d9457162" : "#ed17252e"
        border.color: "#779bd9b7"
        Text { anchors.centerIn: parent; text: root.fixing ? "✓ Fixed!" : "⚒ Repair"; color: "#d8f3e3"; font.pixelSize: 11 }
    }
    MouseArea {
        anchors.fill: parent
        enabled: !root.fixing
        cursorShape: Qt.PointingHandCursor
        onClicked: { root.fixing = true; finish.restart() }
    }
    Timer { id: finish; interval: 280; onTriggered: { root.repaired(); retry.restart() } }
    // If a save fails, keep the crack repairable instead of leaving an invisible input target.
    Timer { id: retry; interval: 1600; onTriggered: root.fixing = false }
}
