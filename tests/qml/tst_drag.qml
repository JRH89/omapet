import QtQuick
import QtTest
import "../.." as Pet
Item {
    width: 300; height: 200
    QtObject {
        id: fake
        property bool dragging: false
        property int saves: 0
        property real dx: 0
        property real dy: 0
        function moveBy(x,y) { dx += x; dy += y }
        function savePosition() { saves++ }
    }
    Pet.PetDragArea { id: area; anchors.fill: parent; desktop: fake; onTapped: fake.dx = -999 }
    TestCase {
        name: "PetDragging"; when: windowShown
        function test_drag_saves_on_release() {
            mousePress(area, 30, 30)
            mouseMove(area, 60, 50, 100)
            compare(fake.dragging, true)
            compare(fake.saves, 0)
            mouseRelease(area, 60, 50)
            compare(fake.dragging, false)
            compare(fake.saves, 1)
            verify(fake.dx > 0)
        }
        function test_tap_does_not_save() {
            let before = fake.saves
            mouseClick(area, 20, 20)
            compare(fake.saves, before)
            compare(fake.dx, -999)
        }
    }
}
