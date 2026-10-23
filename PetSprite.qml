import QtQuick

Item {
    id: root
    property string mood: "happy"
    property string character: "cat"
    property string effect: ""
    property int frame: 0
    property bool animated: true
    implicitWidth: 144
    implicitHeight: 126
    readonly property var palettes: ({cat: "#e8c9ad", fox: "#efa76e", bunny: "#d4b5e8", frog: "#a6cf72", bear: "#cda67f", owl: "#93b9dd", slime: "#84d8cf", robot: "#c1c8d8", penguin: "#526b85", snake: "#97ce79", gopher: "#ba936d", duck: "#f5d461", octocat: "#ab9dd9", android: "#a4c639", crab: "#f18a61", whale: "#6bb9e8", elephant: "#8ba4ce", camel: "#d5b17d", beaver: "#8bbcb2", bug: "#df87b2"})
    Timer { interval: root.effect === "run" ? 50 : 100; running: root.visible && root.animated; repeat: true; onTriggered: { root.frame++; art.requestPaint() } }
    onMoodChanged: art.requestPaint()
    onCharacterChanged: art.requestPaint()
    onEffectChanged: art.requestPaint()
    Canvas {
        id: art
        width: 72; height: 63
        anchors.centerIn: parent
        scale: Math.min(root.width / width, root.height / height)
        // Draw on a small fixed grid, then scale without filtering for visible pixel edges.
        canvasSize: Qt.size(72, 63)
        smooth: false
        onPaint: {
            let c = getContext("2d"); c.reset();
            let scale = Math.min(canvasSize.width / 144, canvasSize.height / 126);
            c.scale(scale, scale); c.translate(12, 8);
            let f = root.frame, kind = root.character;
            let eating = root.effect === "feed", washing = root.effect === "clean";
            let asleep = root.mood === "sleeping";
            function rect(x,y,w,h,col) { c.fillStyle=col; c.fillRect(x,y,w,h) }
            function oval(x,y,w,h,col) { c.fillStyle=col; c.beginPath(); c.ellipse(x,y,w,h); c.fill() }
            function tri(x,y,w,h,col) { c.fillStyle=col; c.beginPath(); c.moveTo(x,y+h); c.lineTo(x+w/2,y); c.lineTo(x+w,y+h); c.closePath(); c.fill() }
            function line(x1,y1,x2,y2,col,w) { c.strokeStyle=col; c.lineWidth=w || 1.5; c.lineCap="round"; c.beginPath(); c.moveTo(x1,y1); c.lineTo(x2,y2); c.stroke() }
            function rounded(x,y,w,h,r,col) {
                c.fillStyle=col; c.beginPath(); c.moveTo(x+r,y); c.lineTo(x+w-r,y);
                c.quadraticCurveTo(x+w,y,x+w,y+r); c.lineTo(x+w,y+h-r);
                c.quadraticCurveTo(x+w,y+h,x+w-r,y+h); c.lineTo(x+r,y+h);
                c.quadraticCurveTo(x,y+h,x,y+h-r); c.lineTo(x,y+r);
                c.quadraticCurveTo(x,y,x+r,y); c.closePath(); c.fill();
            }
            function eye(x,y) {
                if (asleep || f % 55 >= 52) {
                    c.strokeStyle="#29323a"; c.lineWidth=2.5; c.lineCap="round";
                    c.beginPath(); c.moveTo(x-4,y); c.quadraticCurveTo(x,y+4,x+4,y); c.stroke();
                } else {
                    oval(x-4.5,y-6,9,12,"#29323a"); oval(x-2.5,y-4.5,3,3.5,"#fff7e9");
                }
            }
            function smile(x,y) {
                if (root.mood === "sad" || root.mood === "lonely" || root.mood === "sick") {
                    c.strokeStyle="#634d46"; c.lineWidth=2;
                    c.beginPath(); c.moveTo(x-7,y+5); c.quadraticCurveTo(x,y-3,x+7,y+5); c.stroke(); return;
                }
                if (eating) { oval(x-5,y-2,10,4+(f%3)*2,"#563e3c"); return }
                c.strokeStyle="#634d46"; c.lineWidth=1.5; c.lineCap="round";
                c.beginPath(); c.moveTo(x,y-2); c.lineTo(x,y+2);
                c.quadraticCurveTo(x-4,y+6,x-7,y+2); c.moveTo(x,y+2);
                c.quadraticCurveTo(x+4,y+6,x+7,y+2); c.stroke();
            }
            oval(22, 96, 76, 9, "#10232b");
            c.save();
            let bob = root.effect === "run" ? (kind === "snake" ? Math.sin(f * 0.6) * 2 : Math.abs(Math.sin(f * 0.8)) * -8) : asleep ? Math.sin(f/8) : Math.sin(f/4)*2;
            c.translate(eating ? Math.sin(f*1.5)*2 : 0, eating ? Math.abs(Math.sin(f/2))*-5 : bob);
            let body = root.mood === "sick" ? "#c5b86c" : root.mood === "departed" ? "#8c98a3" : (root.palettes[kind] || root.palettes.cat);
            if (kind === "octocat") {
                tri(26,15,29,34,body); tri(68,15,29,34,body);
                oval(24,28,74,53,body); eye(46,51); eye(76,51); smile(61,64);
                for(let i=0;i<5;i++) {
                    let x=30+i*15, wave=Math.sin(f/4+i)*7;
                    line(61,77,x,91+wave,body,9); oval(x-5,88+wave,11,7,body);
                }
            } else if (kind === "android") {
                line(40,27,32,14,body,3); line(81,27,89,14,body,3);
                rounded(28,27,66,38,18,body); eye(46,45); eye(76,45);
                rect(28,63,66,28,body); rounded(12,62,12,29,5,body); rounded(98,62,12,29,5,body);
                rounded(37,86,15,17,5,body); rounded(70,86,15,17,5,body);
            } else if (kind === "crab") {
                for(let i=0;i<3;i++) {
                    line(34,69+i*7,17-i*3,83+i*6,body,5);
                    line(88,69+i*7,105+i*3,83+i*6,body,5);
                }
                line(32,62,16,42,body,7); line(90,62,106,42,body,7);
                oval(7,28,21,22,body); oval(95,28,21,22,body);
                oval(27,48,69,42,body); line(43,55,43,35,body,5); line(79,55,79,35,body,5);
                eye(43,35); eye(79,35); smile(61,72);
            } else if (kind === "whale") {
                oval(15,47,86,47,body); tri(91,44,28,35,body);
                oval(25,72,63,19,"#d0eafa"); eye(37,64); smile(51,78);
                for(let i=0;i<3;i++) rect(32+i*15,32,12,12,"#4394c7");
                rect(47,17,12,12,"#4394c7"); line(17,58,11,44,body,6);
            } else if (kind === "elephant") {
                oval(25,56,74,40,body); oval(14,25,43,45,body); oval(68,25,43,45,body);
                oval(33,24,56,48,body); eye(46,45); eye(76,45);
                rounded(53,54,16,38,7,body); line(61,87,76,82,body,9);
                rect(30,84,18,16,body); rect(77,84,18,16,body);
            } else if (kind === "camel") {
                oval(20,59,76,31,body); oval(32,42,31,39,body);
                rounded(80,30,15,53,6,body); oval(77,23,30,23,body); eye(93,31);
                line(30,83,25,101,body,8); line(76,83,81,101,body,8);
                oval(48,65,25,16,"#ead1a5");
            } else if (kind === "beaver") {
                oval(80,65,35,33,"#597f79"); line(88,72,104,89,"#87a9a1",2);
                oval(26,51,64,45,body); oval(24,16,19,19,body); oval(80,16,19,19,body);
                oval(27,25,67,49,body); eye(45,44); eye(77,44); smile(61,57);
                rect(54,61,6,10,"#fff4db"); rect(62,61,6,10,"#fff4db");
                oval(29,91,24,10,body); oval(71,91,24,10,body);
            } else if (kind === "bug") {
                line(43,30,33,14,body,3); line(78,30,88,14,body,3);
                for(let i=0;i<3;i++) { line(35,58+i*10,19,52+i*16,body,4); line(86,58+i*10,102,52+i*16,body,4) }
                oval(31,42,59,57,body); line(61,52,61,93,"#834c6c",2);
                oval(30,26,61,34,body); eye(46,41); eye(76,41); smile(61,51);
                oval(43,68,9,9,"#834c6c"); oval(71,79,9,9,"#834c6c");
            } else if (kind === "cat") {
                // A seated kitten: curled tail, little paws, oversized round head.
                c.strokeStyle=body; c.lineWidth=13; c.lineCap="round";
                c.beginPath(); c.moveTo(79,85); c.bezierCurveTo(112,100,111,65,97,69); c.stroke();
                c.strokeStyle="#b38a70"; c.lineWidth=3;
                c.beginPath(); c.moveTo(99,78); c.quadraticCurveTo(105,72,99,69); c.stroke();
                oval(37,62,47,36,body); oval(47,69,27,25,"#fff0dc");
                oval(34,86,24,13,body); oval(62,86,24,13,body);
                line(45,92,45,96,"#c19b80",1); line(72,92,72,96,"#c19b80",1);
                tri(27,14,28,37,body); tri(67,14,28,37,body);
                tri(33,23,15,23,"#e9aeb0"); tri(74,23,15,23,"#e9aeb0");
                oval(24,33,73,48,body); oval(29,55,26,23,"#f5dbc5"); oval(67,55,25,23,"#f5dbc5");
                line(54,36,56,42,"#bb9479",3); line(61,35,61,42,"#bb9479",3); line(68,36,66,42,"#bb9479",3);
                eye(44,55); eye(77,55);
                oval(33,63,11,5,"#eeb3ad"); oval(78,63,11,5,"#eeb3ad");
                tri(56,62,9,6,"#cd8e94"); smile(60.5,68);
                line(36,66,21,63,"#aa826e",1); line(36,70,20,71,"#aa826e",1);
                line(84,66,100,63,"#aa826e",1); line(84,70,101,71,"#aa826e",1);
            } else if (kind === "fox") {
                // A sweeping tail sits behind the body; cream cheeks taper to the nose.
                c.fillStyle=body; c.beginPath(); c.moveTo(74,90);
                c.bezierCurveTo(101,108,117,82,108,55); c.bezierCurveTo(103,73,85,68,74,90); c.fill();
                c.fillStyle="#fff0d5"; c.beginPath(); c.moveTo(103,74);
                c.quadraticCurveTo(112,67,108,55); c.quadraticCurveTo(105,64,98,68); c.closePath(); c.fill();
                oval(37,64,45,34,body); tri(44,66,31,26,"#fff0d5");
                oval(35,88,21,11,"#654b43"); oval(64,88,21,11,"#654b43");
                tri(24,7,30,45,body); tri(67,7,30,45,body);
                tri(26,8,14,22,"#654b43"); tri(81,8,14,22,"#654b43");
                tri(31,20,17,25,"#d98e88"); tri(73,20,17,25,"#d98e88");
                c.fillStyle=body; c.beginPath(); c.moveTo(25,43);
                c.quadraticCurveTo(60,27,96,43); c.lineTo(100,59); c.lineTo(84,73);
                c.quadraticCurveTo(60,89,36,73); c.lineTo(20,59); c.closePath(); c.fill();
                c.fillStyle="#fff0d5"; c.beginPath(); c.moveTo(23,57); c.quadraticCurveTo(42,58,60,72);
                c.quadraticCurveTo(78,58,97,57); c.lineTo(82,74); c.quadraticCurveTo(60,89,38,74); c.closePath(); c.fill();
                eye(43,53); eye(78,53); oval(34,61,9,4,"#eca99a"); oval(79,61,9,4,"#eca99a");
                oval(56,68,9,6,"#463d3e"); smile(60.5,75);
            } else if (kind === "duck") {
                // Rubber-duck silhouette: round head, wide bill, plump body, upturned tail.
                c.fillStyle=body; c.beginPath(); c.moveTo(77,66);
                c.quadraticCurveTo(99,66,108,48); c.quadraticCurveTo(110,84,83,91); c.closePath(); c.fill();
                oval(27,53,73,42,body); oval(28,24,43,44,body);
                oval(35,28,13,6,"#fff1a4");
                oval(48,64,33,21,"#e6b842"); oval(47,63,29,17,"#f9de78");
                c.strokeStyle="#d9ac3d"; c.lineWidth=1.5; c.beginPath();
                c.moveTo(51,75); c.quadraticCurveTo(64,84,76,74); c.stroke();
                eye(45,42);
                oval(10,48,29,12,"#ed9b49");
                oval(14,55+(eating ? f%3*2 : 0),23,7,"#e58a3e");
                line(13,56,35,56,"#c77638",1.2);
                oval(29,50,3,2,"#b7753d"); oval(42,51,8,4,"#eeb697");
            } else if (kind === "penguin") {
                oval(29,29,63,67,body); oval(19,55,17,33,body); oval(86,55,17,33,body);
                oval(40,53,43,39,"#f5efe0");
                oval(34,37,29,34,"#f5efe0"); oval(59,37,29,34,"#f5efe0");
                eye(46,51); eye(76,51);
                oval(33,59,9,4,"#e7b5ae"); oval(80,59,9,4,"#e7b5ae");
                oval(54,61,15,8+(eating ? f%3*2 : 0),"#eeb05e");
                oval(28,89,28,11,"#eeb05e"); oval(66,89,28,11,"#eeb05e");
            } else if (kind === "snake") {
                let sway = Math.sin(f / 5) * (root.effect === "run" ? 5 : 2);
                // Outlined overlapping coils, raised neck, and a rounded tapered head.
                oval(20,77,82,23,"#5e925a"); oval(23,77,76,19,body);
                oval(29,68,65,23,"#5e925a"); oval(31,68,61,18,body);
                c.strokeStyle="#d5e9ac"; c.lineWidth=3; c.lineCap="round";
                c.beginPath(); c.moveTo(34,84); c.quadraticCurveTo(61,94,88,83); c.stroke();
                c.fillStyle=body; c.beginPath(); c.moveTo(47,79);
                c.bezierCurveTo(36,65,55+sway,64,49+sway,52); c.lineTo(72+sway,52);
                c.bezierCurveTo(84+sway,68,59,68,70,82); c.closePath(); c.fill();
                c.strokeStyle="#d5e9ac"; c.lineWidth=9;
                c.beginPath(); c.moveTo(62+sway,57); c.bezierCurveTo(70+sway,68,51,70,61,81); c.stroke();
                c.save(); c.translate(sway,0);
                oval(29,28,64,38,body); oval(33,47,56,20,"#cbe4a4");
                oval(56,31,9,4,"#79af68"); oval(62,36,7,3,"#79af68");
                eye(45,43); eye(77,43);
                oval(35,53,9,4,"#dfb9a0"); oval(78,53,9,4,"#dfb9a0");
                oval(54,50,2,2,"#57824d"); oval(67,50,2,2,"#57824d");
                if (eating) oval(56,57,10,4+(f%3)*2,"#3d6443");
                else {
                    c.strokeStyle="#57824d"; c.lineWidth=1.5; c.beginPath(); c.moveTo(47,56); c.quadraticCurveTo(61,65,76,56); c.stroke();
                    if (!asleep && f%45<10) {
                        line(61,61,61,72,"#dc8b9e",2); line(61,72,57,76,"#dc8b9e",1.5); line(61,72,65,76,"#dc8b9e",1.5);
                    }
                }
                c.restore();
                oval(31,75,7,3,"#76ab67"); oval(79,72,7,3,"#76ab67");
            } else if (kind === "gopher") {
                oval(27,21,22,25,body); oval(73,21,22,25,body);
                oval(32,26,12,13,"#e1b8a0"); oval(78,26,12,13,"#e1b8a0");
                oval(38,63,46,33,body); oval(46,72,29,22,"#e4caa8");
                oval(21,34,80,45,body); oval(19,52,31,26,body); oval(72,52,31,26,body);
                oval(37,57,47,25,"#e4caa8"); eye(44,51); eye(78,51);
                oval(55,60,11,7,"#624936");
                if (eating) smile(60,71);
                else { line(49,70,72,70,"#8f694d",1.5); rounded(54,69,6,10,1,"#fff4db"); rounded(62,69,6,10,1,"#fff4db") }
                oval(27,59,10,5,"#dca99b"); oval(85,59,10,5,"#dca99b");
                oval(30,87,25,12,body); oval(68,87,25,12,body);
            } else if (kind === "slime") {
                c.fillStyle=body; c.beginPath(); c.moveTo(18,86);
                c.bezierCurveTo(17,66,28,34,51,32); c.quadraticCurveTo(67,29,83,45);
                c.bezierCurveTo(94,59,101,71,104,87); c.quadraticCurveTo(97,101,83,95);
                c.quadraticCurveTo(66,103,53,97); c.quadraticCurveTo(33,103,18,92); c.closePath(); c.fill();
                oval(31,43,18,9,"#c7f1e0"); oval(28,56,6,5,"#c7f1e0");
                eye(46,66); eye(78,66); smile(62,80);
                oval(31,76,11,5,"#efb9bd"); oval(81,76,11,5,"#efb9bd");
            } else if (kind === "bunny") {
                oval(25,78,18,17,"#eeddf5");
                oval(38,60,46,37,body); oval(47,70,28,25,"#eee0f4");
                oval(30,86,26,13,body); oval(66,86,26,13,body);
                oval(30,3,18,48,body); oval(74,3,18,48,body);
                oval(35,10,8,31,"#e8b2ca"); oval(79,10,8,31,"#e8b2ca");
                oval(24,34,75,44,body); eye(44,54); eye(79,54);
                oval(33,62,11,5,"#eeb9cd"); oval(80,62,11,5,"#eeb9cd");
                oval(57,61,9,6,"#c28fae"); smile(61,68);
            } else if (kind === "bear") {
                oval(37,61,47,36,body); oval(46,69,29,26,"#e3c4a3");
                oval(24,21,26,27,body); oval(72,21,26,27,body);
                oval(30,27,14,14,"#916c54"); oval(78,27,14,14,"#916c54");
                oval(24,34,75,45,body); oval(43,56,37,24,"#e3c4a3");
                eye(43,52); eye(79,52); oval(55,59,13,9,"#624a3c"); smile(61,70);
                oval(31,61,9,5,"#dca79b"); oval(83,61,9,5,"#dca79b");
                oval(30,85,26,14,body); oval(66,85,26,14,body);
                oval(37,89,12,6,"#a77d61"); oval(73,89,12,6,"#a77d61");
            } else if (kind === "frog") {
                oval(27,65,69,30,body); oval(37,69,48,23,"#d6e6ab");
                oval(20,83,32,15,body); oval(70,83,32,15,body);
                oval(25,24,28,34,body); oval(69,24,28,34,body);
                oval(20,41,82,36,body); oval(28,54,67,20,"#cfe0a5");
                eye(40,40); eye(83,40);
                oval(27,57,12,5,"#e4bda5"); oval(85,57,12,5,"#e4bda5");
                if (eating) oval(55,61,13,6+(f%3)*2,"#4a6d44");
                else { c.strokeStyle="#5f8150"; c.lineWidth=2; c.beginPath(); c.moveTo(44,60); c.quadraticCurveTo(61,73,79,60); c.stroke() }
                oval(48,30,5,3,"#8db260"); oval(67,31,6,3,"#8db260");
            } else if (kind === "owl") {
                tri(26,18,25,32,body); tri(72,18,25,32,body);
                oval(24,33,76,64,body); oval(18,56,20,33,"#6f96be"); oval(84,56,20,33,"#6f96be");
                oval(36,64,51,28,"#c2d7df");
                oval(29,39,33,34,"#f1ebd3"); oval(61,39,33,34,"#f1ebd3");
                eye(46,54); eye(77,54);
                tri(56,65,12,10+(eating ? f%3 : 0),"#eabb6c");
                oval(30,65,9,4,"#e6b5b0"); oval(85,65,9,4,"#e6b5b0");
                line(48,82,50,84,"#87a9c2",2); line(61,83,63,85,"#87a9c2",2); line(74,82,76,84,"#87a9c2",2);
                oval(35,92,19,8,"#eabb6c"); oval(70,92,19,8,"#eabb6c");
            } else if (kind === "robot") {
                rect(58,13,5,20,"#8796ab"); oval(54,9,13,11,"#eca9af");
                rounded(37,66,48,29,6,body); rounded(47,71,28,17,3,"#738da0");
                rounded(17,44,12,24,4,"#8796ab"); rounded(93,44,12,24,4,"#8796ab");
                rounded(25,31,72,42,10,body); rounded(32,38,58,28,6,"#344a58");
                if (asleep || f%55>=52) { line(42,52,50,52,"#a9e4cf",3); line(72,52,80,52,"#a9e4cf",3) }
                else { rounded(41,45,10,13,3,"#a9e4cf"); rounded(71,45,10,13,3,"#a9e4cf"); rect(44,46,3,3,"#effcf0"); rect(74,46,3,3,"#effcf0") }
                rect(55,60,11,2,"#a9e4cf"); rect(57,77,8,3,"#a9e4cf"); rect(60,74,3,9,"#a9e4cf");
                rounded(31,88,24,11,4,"#8796ab"); rounded(68,88,24,11,4,"#8796ab");
            }
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
            if (root.effect === "bonk") {
                for (let i=0;i<3;i++) {
                    let x=25+i*31, y=12+(i%2)*5-(f%3)*2;
                    rect(x-4,y,9,2,"#ffe6a0"); rect(x,y-4,2,10,"#ffe6a0");
                }
            }
            if (root.mood === "sad" || root.mood === "lonely") {
                c.fillStyle="#9ac9e7"; c.font="bold 12px monospace"; c.fillText(root.mood === "sad" ? ":(" : "…",96,20);
                if (root.mood === "sad") oval(85,58+(f%8),4,7,"#9ac9e7");
            }
            if (asleep) { c.fillStyle="#b9d7e4"; c.font="bold 14px monospace"; c.fillText("z",91,27-(f%20)/2); c.fillText("Z",102,16-(f%20)/3) }
        }
    }
}
