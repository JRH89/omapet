import QtQuick

MouseArea {
    id: root
    required property var desktop
    property real pressX: 0
    property real pressY: 0
    property bool moved: false
    signal tapped()
    cursorShape: pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
    preventStealing: true
    onPressed: function(mouse) { pressX = mouse.x; pressY = mouse.y; moved = false; desktop.dragging = true }
    onPositionChanged: function(mouse) {
        if (!pressed) return
        let dx = mouse.x - pressX, dy = mouse.y - pressY
        if (!moved && Math.abs(dx) + Math.abs(dy) < 6) return
        moved = true
        desktop.moveBy(dx, dy)
    }
    onReleased: { desktop.dragging = false; if (moved) desktop.savePosition(); else tapped() }
    onCanceled: { desktop.dragging = false; if (moved) desktop.savePosition() }
}
