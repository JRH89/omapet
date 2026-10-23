// Staged README scenes rendered with the production sprites and mess effects.
import QtQuick
import QtTest
import ".." as Pet

Rectangle {
    id: scene
    width: 960; height: mode === 3 ? 430 : 520
    color: "#111e27"
    property int mode: 0
    property string outputDirectory: ""
    readonly property var headings: ["A little freedom.", "One tiny pet. One big bonk.", "Well… that happened.", "Meet the new developers."]
    readonly property var subtitles: ["Let one companion out, or let the whole household roam.", "Pretend screen cracks. Real cleanup duty.", "Pixel poop happens. Click Clean up to put things right.", "Eight more companions, each with its own silhouette and palette."]
    Text { x: 34; y: 25; text: "O M A P E T   /   DESKTOP ADVENTURES"; color: "#8fac9e"; font.pixelSize: 11; font.letterSpacing: 2 }
    Text { x: 34; y: 52; text: scene.headings[scene.mode]; color: "#edf5ef"; font.pixelSize: 30; font.bold: true }
    Text { x: 34; y: 96; text: scene.subtitles[scene.mode]; color: "#a8bec4"; font.pixelSize: 14 }

    Rectangle {
        visible: scene.mode !== 3
        x: 24; y: 139; width: 912; height: 351; radius: 16; color: "#1a2b35"
        border.color: "#314854"
        // A fictional work surface keeps personal windows out of the documentation.
        Rectangle {
            x: 22; y: 22; width: 570; height: 274; radius: 10; color: "#15222c"; border.color: "#314854"
            Rectangle { x: 1; y: 1; width: parent.width - 2; height: 30; radius: 9; color: "#20343e" }
            Row {
                x: 13; y: 12; spacing: 6
                Repeater { model: ["#d88787", "#d9ba79", "#86b899"]; Rectangle { required property string modelData; width: 7; height: 7; radius: 4; color: modelData } }
            }
            Text { x: 100; y: 10; text: "~/projects/tiny-adventures   ·   care.py"; color: "#a8bec4"; font.family: "monospace"; font.pixelSize: 11 }
            Text {
                x: 23; y: 57; color: "#a6c2c9"; font.family: "monospace"; font.pixelSize: 15; lineHeight: 1.55
                text: "01   def a_good_day(pets):\n02       for pet in pets:\n03           feed(pet)\n04           play(pet)\n05           let_them_explore()\n06\n07   # a little care, a little code"
            }
        }
        Text { x: 26; y: 318; text: "STAGED DEMO · ACTUAL OMAPET SPRITES AND EFFECTS"; color: "#7f9aa7"; font.pixelSize: 10; font.letterSpacing: 1 }
        // Escape: the same run animation used by the desktop and companion windows.
        Item {
            visible: scene.mode === 0; anchors.fill: parent
            Canvas {
                anchors.fill: parent
                onPaint: {
                    let c = getContext("2d"); c.strokeStyle="#557d72"; c.lineWidth=2; c.setLineDash([5,8]);
                    c.beginPath(); c.moveTo(716,230); c.bezierCurveTo(600,310,410,290,394,224); c.bezierCurveTo(380,170,460,170,480,140); c.stroke();
                }
            }
            Rectangle {
                x: 684; y: 36; width: 194; height: 149; radius: 16; color: "#17252e"; border.color: "#426354"
                Text { x: 14; y: 14; text: "HOME SWEET HOME"; color: "#8fac9e"; font.pixelSize: 10 }
                Text { anchors.centerIn: parent; text: "Out exploring…"; color: "#a6beb3"; font.pixelSize: 12 }
                Pet.PetButton { anchors { bottom: parent.bottom; horizontalCenter: parent.horizontalCenter; margins: 12 } width: 160; text: "All out ↗" }
            }
            Pet.PetSprite { x: 390; y: 120; character: "octocat"; effect: "run"; frame: 4; animated: false }
            Pet.PetSprite { x: 553; y: 195; character: "crab"; effect: "run"; frame: 8; animated: false }
            Pet.PetSprite { x: 730; y: 190; character: "android"; effect: "run"; frame: 12; animated: false }
            Rectangle { x: 370; y: 267; width: 170; height: 23; radius: 8; color: "#17252e"; Text { anchors.centerIn: parent; text: "Click a pet to bring it home"; color: "#d8f3e3"; font.pixelSize: 10 } }
        }
        Item {
            visible: scene.mode === 1; anchors.fill: parent
            Pet.CrackEffect { x: 448; y: 45; seed: 73 }
            Pet.CrackEffect { x: 642; y: 88; seed: 24 }
            Pet.PetSprite { x: 714; y: 36; character: "crab"; effect: "bonk"; frame: 5; animated: false }
            Rectangle { x: 657; y: 274; width: 208; height: 25; radius: 8; color: "#17252e"; Text { anchors.centerIn: parent; text: "Repair the messes before going home"; color: "#e9b47f"; font.pixelSize: 10 } }
        }
        Item {
            visible: scene.mode === 2; anchors.fill: parent
            Pet.CrackEffect { x: 552; y: 116; messKind: "poop" }
            Pet.PetSprite { x: 706; y: 128; character: "beaver"; frame: 4; animated: false }
            Rectangle { x: 612; y: 43; width: 257; height: 46; radius: 10; color: "#293f40"; border.color: "#426354"; Text { anchors.centerIn: parent; text: "Oops! One little mess to clean up."; color: "#d8f3e3"; font.pixelSize: 12 } }
        }
    }
    Grid {
        visible: scene.mode === 3
        x: 30; y: 144; columns: 4; rowSpacing: 8; columnSpacing: 4
        Repeater {
            model: [
                {kind: "octocat", name: "Octocat", cue: "Pull requests & tentacles"},
                {kind: "android", name: "Android", cue: "A little green robot"},
                {kind: "crab", name: "Rust crab", cue: "Fearless little Ferris"},
                {kind: "whale", name: "Docker whale", cue: "Ships with tiny containers"},
                {kind: "elephant", name: "PostgreSQL elephant", cue: "A trunk full of queries"},
                {kind: "camel", name: "Perl camel", cue: "More than one way to roam"},
                {kind: "beaver", name: "Beaver", cue: "A busy little database friend"},
                {kind: "bug", name: "Bug", cue: "A feature with six legs"}
            ]
            Item {
                required property var modelData
                width: 222; height: 129
                Pet.PetSprite { width: 116; height: 90; anchors.horizontalCenter: parent.horizontalCenter; character: parent.modelData.kind; animated: false; frame: 4 }
                Text { y: 88; width: parent.width; text: parent.modelData.name; horizontalAlignment: Text.AlignHCenter; color: "#edf5ef"; font.pixelSize: 13; font.bold: true }
                Text { y: 109; width: parent.width; text: parent.modelData.cue; horizontalAlignment: Text.AlignHCenter; color: "#a8bec4"; font.pixelSize: 10 }
            }
        }
    }
    TestCase {
        name: "ReadmeShowcase"
        when: windowShown
        function test_capture() {
            let names = ["desktop-escape", "desktop-cracks", "desktop-poop", "developer-pets"]
            verify(scene.outputDirectory.length > 0, "Set outputDirectory in the capture wrapper")
            for (let i = 0; i < names.length; i++) {
                scene.mode = i
                wait(150)
                grabImage(scene).save(scene.outputDirectory + "/" + names[i] + ".png")
            }
        }
    }
}
