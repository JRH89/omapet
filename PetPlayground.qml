pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Wayland
import "Playground.js" as Games

Item {
    id: root
    required property var petModel
    required property var targetScreen
    readonly property var eligible: Games.roster(petModel && petModel.pet ? petModel.pet.pets || [] : [])
    readonly property string rosterKey: eligible.map(p => p.id).join("/")
    property var groups: []
    property var poses: ({})
    property var scenes: []
    property double started: Date.now()
    property double elapsed: 0
    property int submittedRound: -1
    property bool wasVisible: false
    readonly property int count: eligible.length
    function rebuild() {
        if (!targetScreen || !petModel || !petModel.pet) return
        groups = Games.arrange(eligible, targetScreen.width, targetScreen.height)
        started = Date.now()
        elapsed = 0
        submittedRound = -1
        update()
    }
    function pose(petId) { return poses[petId] || null }
    function update() {
        elapsed = Math.max(0, (Date.now() - started) / 1000)
        let round = Math.floor(elapsed / 90), phase = elapsed % 90
        let chosen = groups.length ? round % groups.length : -1
        let p = petModel.pet
        let ready = p.overlay === true && !p.repairing_cracks && (p.cracks || []).length < 4
            && Date.now() / 1000 - (p.last_team_bonk_at || 0) >= 75
        let nextPoses = {}, nextScenes = []
        for (let i = 0; i < groups.length; i++) {
            let sample = Games.sample(groups[i], elapsed, (ready || submittedRound === round) && i === chosen)
            for (let actor of sample.actors) nextPoses[actor.id] = actor
            nextScenes.push({group: groups[i], state: sample})
        }
        poses = nextPoses
        scenes = nextScenes
        if (ready && chosen >= 0 && phase >= 72 && phase < 76 && submittedRound !== round
            && Date.now() / 1000 - (p.last_team_bonk_at || 0) >= 90
            && Date.now() / 1000 - (p.last_bonk_at || 0) >= 15) {
            submittedRound = round
            let g = groups[chosen]
            petModel.run(["team-bonk", String(Math.round(g.x + g.width * .56)),
                String(Math.round(g.y + g.height * .48)), "--screen", targetScreen.name,
                "--pets"].concat(g.members.map(member => member.id)))
        }
    }
    onRosterKeyChanged: rebuild()
    onTargetScreenChanged: rebuild()
    Connections {
        target: root.petModel
        function onPetChanged() {
            let visible = root.petModel.pet.overlay === true
            if (visible && !root.wasVisible) root.rebuild()
            root.wasVisible = visible
        }
    }
    Connections {
        target: root.targetScreen
        ignoreUnknownSignals: true
        function onWidthChanged() { root.rebuild() }
        function onHeightChanged() { root.rebuild() }
    }
    Timer {
        interval: 40; running: root.petModel.pet.overlay === true && root.count >= 2; repeat: true
        onTriggered: root.update()
    }
    Variants {
        model: root.groups
        delegate: Component {
            PanelWindow {
                id: overlay
                readonly property var scene: root.scenes[modelData.index] || ({state: Games.sample(modelData, 0, false)})
                required property var modelData
                screen: root.targetScreen
                visible: root.petModel.pet.overlay === true && root.count >= 2
                anchors { top: true; left: true }
                margins.left: Math.round(modelData.x)
                margins.top: Math.round(modelData.y)
                implicitWidth: modelData.width
                implicitHeight: modelData.height
                color: "transparent"; exclusiveZone: 0
                mask: Region {} // Courts and balls never intercept desktop clicks.
                WlrLayershell.layer: WlrLayer.Top
                WlrLayershell.namespace: "omapet-playground"
                PlaygroundScene { group: overlay.modelData; snapshot: overlay.scene.state }
            }
        }
    }
    Component.onCompleted: { wasVisible = petModel.pet.overlay === true; rebuild() }
}
