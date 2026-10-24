import QtQuick
import QtTest
import "../../Playground.js" as Games
import "../.." as Pet

Rectangle {
    id: scene
    width: 960; height: 400; color: "#17252e"
    property var currentGroup: Games.arrange(members(4), 900, 360)[0]
    property var snapshot: Games.sample(currentGroup, 9.2, false)
    function members(count) {
        let result = []
        for (let i = 0; i < count; i++) result.push({id: String(i).padStart(2, "0"), roaming: true, can_roam: true})
        return result
    }
    Pet.PlaygroundScene { x: 20; y: 20; group: scene.currentGroup; snapshot: scene.snapshot }
    TestCase {
        name: "GroupPlayground"; when: windowShown
        function test_pairs_fours_and_single_odd_pet() {
            compare(Games.arrange(scene.members(1), 1920, 1080).length, 0)
            compare(Games.arrange(scene.members(2), 1920, 1080)[0].game, "catch")
            compare(Games.arrange(scene.members(3), 1920, 1080)[0].members.length, 3)
            let six = Games.arrange(scene.members(6), 1920, 1080)
            compare(six.length, 2)
            compare(six[0].game, "four-square")
            compare(six[1].game, "catch")
        }
        function test_stable_rosters_and_unfit_pets_are_excluded() {
            let pets = scene.members(6)
            compare(JSON.stringify(Games.arrange(pets, 900, 600)), JSON.stringify(Games.arrange(pets.slice().reverse(), 900, 600)))
            pets[0].roaming = false
            pets[1].can_roam = false
            compare(Games.roster(pets).length, 4)
            compare(Games.arrange(pets, 900, 600)[0].members.length, 4)
        }
        function test_groups_stay_on_small_and_large_screens() {
            for (let dim of [[640,480],[1920,1080],[3840,2160]]) {
                let groups = Games.arrange(scene.members(24), dim[0], dim[1])
                compare(groups.length, 6)
                for (let g of groups) {
                    verify(g.x >= 0 && g.y >= 0)
                    verify(g.x + g.width <= dim[0])
                    verify(g.y + g.height <= dim[1])
                    for (let t of [0, 20, 65, 72, 76, 100]) {
                        let state = Games.sample(g, t, true)
                        for (let actor of state.actors) {
                            verify(actor.x >= 0 && actor.y >= 0)
                            verify(actor.x + actor.size <= dim[0])
                            verify(actor.y + actor.size + 22 <= dim[1])
                        }
                    }
                }
            }
        }
        function test_balls_travel_and_team_rally_returns_to_play() {
            let group = Games.arrange(scene.members(2), 900, 600)[0]
            let start = Games.sample(group, 0, false).ball
            let caught = Games.sample(group, 1.8, false).ball
            verify(caught.x > start.x)
            compare(Games.sample(group, 3.6, false).ball.x, start.x)
            compare(Games.sample(group, 65, true).mode, "rally")
            compare(Games.sample(group, 72, true).mode, "bonk")
            compare(Games.sample(group, 78, true).mode, "catch")
            compare(Games.sample(group, 72, false).mode, "catch")
        }
        function test_keep_away_handoffs() {
            for (let count of [3,5,7,9,23]) {
                let groups = Games.arrange(scene.members(count), 1920, 1080)
                compare(groups.reduce((n,g) => n + g.members.length, 0), count)
                let g = groups.filter(g => g.game === "keep-away")[0]
                for (let t = 0; t < 40; t += 8) {
                    compare(Games.sample(g, t, false).loser, Games.sample(g, t + 8, false).chaser)
                }
            }
        }
        function test_motion_is_bounded_and_does_not_overshoot() {
            let next = Games.approach(0, 0, 300, 400, .1, 200)
            fuzzyCompare(Math.sqrt(next.x*next.x + next.y*next.y), 20, .001)
            next = Games.approach(0, 0, 3, 4, 1, 200)
            compare(next.x, 3); compare(next.y, 4)
        }
        function test_game_visuals_render() {
            for (let size of [2,3,4,5]) for (let time of [4,65,72]) {
                scene.currentGroup = Games.arrange(scene.members(size), 900, 360)[0]
                scene.snapshot = Games.sample(scene.currentGroup, time, true)
                wait(5)
                compare(grabImage(scene).width, 960)
            }
        }
    }
}
