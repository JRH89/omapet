import QtQuick

Item {
    id: root
    property string mood: "happy"
    property string character: "cat"
    property string effect: ""
    property int frame: 0
    implicitWidth: 144
    implicitHeight: 126
    readonly property var palettes: ({cat: "#9bd9b7", fox: "#efa76e", bunny: "#d4b5e8", frog: "#a6cf72", bear: "#cda67f", owl: "#93b9dd", slime: "#84d8cf", robot: "#c1c8d8", penguin: "#526b85", snake: "#97ce79", gopher: "#ba936d"})
    Timer { interval: root.effect === "run" ? 50 : 100; running: root.visible; repeat: true; onTriggered: { root.frame++; art.requestPaint() } }
    onMoodChanged: art.requestPaint()
    onCharacterChanged: art.requestPaint()
    onEffectChanged: art.requestPaint()
    Canvas {
        id: art
        anchors.fill: parent
        onPaint: {
            let c = getContext("2d"); c.reset();
            let scale = Math.min(width / 144, height / 126);
            c.scale(scale, scale); c.translate(12, 8);
            let f = root.frame, kind = root.character;
            let eating = root.effect === "feed", washing = root.effect === "clean";
            let asleep = root.mood === "sleeping";
            function rect(x,y,w,h,col) { c.fillStyle=col; c.fillRect(x,y,w,h) }
            function oval(x,y,w,h,col) { c.fillStyle=col; c.beginPath(); c.ellipse(x,y,w,h); c.fill() }
            function tri(x,y,w,h,col) { c.fillStyle=col; c.beginPath(); c.moveTo(x,y+h); c.lineTo(x+w/2,y); c.lineTo(x+w,y+h); c.closePath(); c.fill() }
            oval(22, 96, 76, 9, "#10232b");
            c.save();
            let bob = root.effect === "run" ? (kind === "snake" ? Math.sin(f * 0.6) * 2 : Math.abs(Math.sin(f * 0.8)) * -8) : asleep ? Math.sin(f/8) : Math.sin(f/4)*2;
            c.translate(eating ? Math.sin(f*1.5)*2 : 0, eating ? Math.abs(Math.sin(f/2))*-5 : bob);
            let body = root.mood === "sick" ? "#c5b86c" : root.mood === "departed" ? "#8c98a3" : (root.palettes[kind] || root.palettes.cat);
            if (kind === "penguin") {
                oval(27,25,66,72,body);
                oval(17,49,17,40,body); oval(86,49,17,40,body);
                oval(37,48,46,45,"#e9eee0");
                oval(33,39,24,29,"#e9eee0"); oval(63,39,24,29,"#e9eee0");
                oval(29,90,25,10,"#edb76e"); oval(66,90,25,10,"#edb76e");
            } else if (kind === "snake") {
                let sway = Math.sin(f / 3) * (root.effect === "run" ? 6 : 2);
                oval(19,77,83,22,body); oval(28,68,64,21,body);
                oval(44+sway,49,30,37,body); oval(26,34,68,39,body);
                oval(32,77,58,8,"#c4e8a4");
                rect(51,91,9,3,"#70aa5d"); rect(77,82,8,3,"#70aa5d");
            } else if (kind === "gopher") {
                oval(25,21,20,25,body); oval(75,21,20,25,body);
                oval(29,26,12,14,"#e1b8a0"); oval(79,26,12,14,"#e1b8a0");
                oval(23,35,74,58,body); oval(16,52,29,29,body); oval(75,52,29,29,body);
                oval(37,59,46,30,"#e2c7a2");
                oval(25,86,25,11,body); oval(70,86,25,11,body);
            } else if (kind === "slime") {
                oval(20, 35, 80, 64, body); rect(24,68,72,25,body);
                oval(33,42,16,8,"#bef1e4");
            } else {
                if (kind === "bunny") { oval(31,0,15,54,body); oval(74,0,15,54,body); oval(35,7,7,30,"#f1c5d7"); oval(78,7,7,30,"#f1c5d7") }
                else if (kind === "bear") { oval(20,22,24,26,body); oval(76,22,24,26,body); oval(26,28,12,12,"#a77962"); oval(82,28,12,12,"#a77962") }
                else if (kind === "frog") { oval(27,24,22,28,body); oval(71,24,22,28,body) }
                else if (kind === "robot") { rect(57,13,6,20,body); oval(54,8,12,12,"#eba8af"); rect(15,50,9,24,"#7d8b9e"); rect(96,50,9,24,"#7d8b9e") }
                else { tri(26,14,23,36,body); tri(71,14,23,36,body); tri(31,23,12,21,"#f1c5c3"); tri(77,23,12,21,"#f1c5c3") }
                if (kind === "owl") { oval(20,35,80,62,body); oval(21,59,14,32,"#6586b0"); oval(85,59,14,32,"#6586b0") }
                else { rect(27,36,66,52,body); rect(20,48,80,30,body) }
                rect(31,84,19,11,body); rect(70,84,19,11,body);
                if (kind === "fox") { tri(17,63,25,25,"#ffe0b5"); tri(78,63,25,25,"#ffe0b5"); tri(47,58,26,22,"#ffe0b5") }
            }
            if (kind === "owl") { oval(32,43,24,27,"#e2e8ce"); oval(64,43,24,27,"#e2e8ce"); tri(55,65,10,10,"#edbd70") }
            let eyeY = kind === "frog" ? 34 : 52;
            let blink = asleep || f % 55 >= 52;
            rect(39, eyeY + (blink ? 7 : 0), 8, blink ? 3 : 10, "#203742");
            rect(73, eyeY + (blink ? 7 : 0), 8, blink ? 3 : 10, "#203742");
            if (kind === "penguin" && !eating) { tri(52,65,16,12,"#edb76e") }
            else if (kind === "gopher" && !eating) { oval(55,64,10,6,"#5e4636"); rect(54,72,5,8,"#fff2d6"); rect(61,72,5,8,"#fff2d6") }
            else if (kind === "snake" && !eating) { rect(55,70,10,3,"#203742"); if(f%35<12) { rect(59,73,3,11,"#e398a5"); rect(56,82,3,4,"#e398a5"); rect(62,82,3,4,"#e398a5") } }
            else if (kind === "robot") { rect(54,73,12,4,"#87c8bd"); rect(58,69,4,12,"#87c8bd") }
            else if (eating) { oval(54,66,12, 4 + (f%3)*3,"#203742") }
            else { rect(55,70,10,3,"#203742") }
            rect(28,64,9,4,"#f1c5c3"); rect(83,64,9,4,"#f1c5c3");
            c.restore();
            if (eating) {
                oval(43,94,35,10,"#e7bf83"); rect(47,98,27,6,"#c49164");
                for(let i=0;i<5;i++) { let t=(f*3+i*13)%32; rect(48+i*5,93-t,3,3,"#eac384") }
            }
            if (washing) {
                for(let i=0;i<8;i++) {
                    let y=100-(f*3+i*17)%105, x=15+(i*31)%95;
                    c.strokeStyle="#b5eff1"; c.lineWidth=2; c.beginPath(); c.ellipse(x,y,7+i%3*3,7+i%3*3); c.stroke();
                    rect(x+2,y+2,2,2,"#ffffff");
                }
            }
            if (asleep) { c.fillStyle="#b9d7e4"; c.font="bold 14px monospace"; c.fillText("z",91,27-(f%20)/2); c.fillText("Z",102,16-(f%20)/3) }
        }
    }
}
