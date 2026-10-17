import QtQuick
import QtTest
import "../.." as Pet

Rectangle {
    id: scene
    width: 240; height: 230; color: "#17252e"
    Pet.CrackEffect { id: crack; x: 40; y: 20; seed: 42 }
    SignalSpy { id: repairs; target: crack; signalName: "repaired" }
    TestCase {
        name: "CrackRepair"; when: windowShown
        function test_repair_animation_emits_once_and_blocks_double_clicks() {
            mouseClick(crack, 80, 80)
            compare(crack.fixing, true)
            compare(repairs.count, 0)
            mouseClick(crack, 80, 80)
            tryCompare(repairs, "count", 1)
            mouseClick(crack, 80, 80)
            wait(350)
            compare(repairs.count, 1)
        }
    }
}
