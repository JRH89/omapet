import QtQuick
import QtQuick.Controls as Controls
import QtTest
import "../.." as Pet

Item {
    id: scene
    width: 300; height: 200
    Pet.PetButton {
        id: button
        x: 40; y: 40
        text: "Let out"
        hint: "Low energy. Let your pet sleep until energy reaches 20."
        available: false
    }
    SignalSpy { id: clicks; target: button; signalName: "clicked" }
    TestCase {
        name: "PetButton"; when: windowShown
        function init() { clicks.clear(); button.available = false; mouseMove(scene, 250, 150) }
        function test_unavailable_button_keeps_tooltip_and_blocks_clicks() {
            mouseMove(button, 20, 12)
            tryCompare(button, "hovered", true)
            compare(button.Controls.ToolTip.text, button.hint)
            tryVerify(function() { return button.Controls.ToolTip.visible }, 2000)
            mouseClick(button, 20, 12)
            compare(clicks.count, 0)
        }
        function test_available_button_clicks() {
            button.available = true
            mouseClick(button, 20, 12)
            compare(clicks.count, 1)
        }
    }
}
