import QtQuick

Item {
    id: root
    property int seed: 1
    property int power: 1
    onPowerChanged: glass.requestPaint()
    property string messKind: "crack"
    onMessKindChanged: glass.requestPaint()
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
            if (root.messKind === "poop") {
                // Deliberately chunky pixels to match the companion artwork.
                let px = width / 2 - 28, py = height / 2 - 20
                let rows = ["00011000", "00111100", "01111100", "01111110", "11111111", "11111111"]
                for (let y=0; y<rows.length; y++) for (let x=0; x<8; x++) if (rows[y][x] === "1") {
                    c.fillStyle = y < 2 ? "#b77a45" : y < 4 ? "#8f5935" : "#69412c"
                    c.fillRect(px+x*7,py+y*7,7,7)
                }
                c.fillStyle="#f6e7cd"; c.fillRect(px+17,py+22,5,5); c.fillRect(px+38,py+22,5,5)
                return
            }
            let state = root.seed % 233280
            function random() { state = (state * 9301 + 49297) % 233280; return state / 233280 }
            let cx = width / 2, cy = height / 2, rays = []
            for (let i = 0; i < 7 + Math.min(3, Math.max(0, root.power - 1)) * 2; i++) {
                let angle = i * Math.PI * 2 / (7 + Math.min(3, Math.max(0, root.power - 1)) * 2) + (random() - 0.5) * 0.35
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
        Text { anchors.centerIn: parent; text: root.fixing ? "✓ Done!" : root.messKind === "poop" ? "✦ Clean up" : "⚒ Repair"; color: "#d8f3e3"; font.pixelSize: 11 }
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
