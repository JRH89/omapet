import QtQuick
import QtTest
import "../.." as Pet

Item {
    width: 800; height: 720
    Rectangle { anchors.fill: parent; color: "#17252e" }
    Grid {
        id: grid
        columns: 5; spacing: 4
        Repeater {
            id: pets
            model: ["cat", "fox", "bunny", "frog", "bear", "owl", "slime", "robot", "penguin", "snake", "gopher", "duck", "octocat", "android", "crab", "whale", "elephant", "camel", "beaver", "bug"]
            Column {
                required property string modelData
                Pet.PetSprite { width: 144; height: 126; character: parent.modelData; animated: false }
                Text { text: parent.modelData; color: "#d8f3e3"; anchors.horizontalCenter: parent.horizontalCenter }
            }
        }
    }
    TestCase {
        name: "PetSprites"; when: windowShown
        function test_all_characters_and_moods_render() {
            compare(pets.count, 20)
            for (let i = 0; i < pets.count; i++) {
                let sprite = pets.itemAt(i).children[0]
                for (let mood of ["happy", "lonely", "sad", "sleeping", "sick"]) {
                    sprite.mood = mood
                    wait(1)
                    let rendered = grabImage(sprite)
                    compare(rendered.width, 144)
                    compare(rendered.height, 126)
                }
                sprite.mood = "happy"
            }
            wait(100)
        }
    }
}
