.pragma library

function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }

// Stable IDs keep a polling refresh from reshuffling games or restarting animations.
function roster(pets) {
    return pets.filter(p => p.roaming && p.can_roam !== false).slice().sort((a, b) => a.id.localeCompare(b.id));
}

function arrange(pets, screenWidth, screenHeight) {
    let members = roster(pets), chunks = [], groups = [];
    while (members.length >= 4 && members.length !== 5) chunks.push(members.splice(0, 4));
    if (members.length === 3 || members.length === 5) chunks.push(members.splice(0));
    while (members.length >= 2) chunks.push(members.splice(0, 2));
    // Odd groups share keep-away so every eligible pet can join.
    let columns = Math.max(1, Math.min(chunks.length, Math.floor(screenWidth / 310)));
    let rows = Math.max(1, Math.ceil(chunks.length / columns));
    let width = Math.min(430, Math.max(120, (screenWidth - 24) / columns));
    let height = Math.min(330, Math.max(120, (screenHeight - 64) / rows));
    let size = Math.min(144, Math.max(54, Math.min(width / 2.6, height / 2.5)));
    for (let i = 0; i < chunks.length; i++) {
        let col = i % columns, row = Math.floor(i / columns);
        groups.push({id: chunks[i].map(p => p.id).join("/"), members: chunks[i],
            game: chunks[i].length % 2 ? "keep-away" : chunks[i].length === 4 ? "four-square" : "catch", index: i, size: size,
            x: Math.max(0, (screenWidth - columns * width) / 2 + col * width),
            y: Math.max(0, (screenHeight - 40 - rows * height) / 2 + row * height),
            width: width, height: height});
    }
    return groups;
}

function slot(group, index) {
    let pad = 12, size = group.size;
    if (group.game === "keep-away") {
        let angle = index * Math.PI * 2 / group.members.length - Math.PI / 2;
        return {x: (group.width - size) / 2 + Math.cos(angle) * (group.width - size - 24) / 2,
                y: (group.height - size - 22) / 2 + Math.sin(angle) * (group.height - size - 46) / 2};
    }
    if (group.game === "catch")
        return {x: index === 0 ? pad : group.width - size - pad, y: (group.height - size) / 2};
    return {x: index % 2 === 0 ? pad : group.width - size - pad,
            y: index < 2 ? pad : group.height - size - 32};
}

function sample(group, elapsed, attack) {
    let phase = (elapsed % 90 + 90) % 90;
    let teaming = attack && phase >= 62 && phase < 76;
    let mode = teaming ? (phase < 71 ? "rally" : "bonk") : group.game;
    let poses = [], size = group.size;
    // Each interception makes the passer who lost possession the next chaser.
    let chaseRound = Math.floor(elapsed / 8), chasePhase = elapsed % 8;
    let chaser = chaseRound % group.members.length;
    let loser = (chaser + 1) % group.members.length;
    let runners = [];
    for (let i = 0; i < group.members.length; i++) if (i !== chaser) runners.push(i);
    let pass = Math.floor(chasePhase / 1.6);
    let source = runners[pass % runners.length], target = runners[(pass + 1) % runners.length];
    if (chasePhase >= 6.4) { source = loser; target = chaser; }
    let chaseU = (chasePhase % 1.6) / 1.6;
    for (let i = 0; i < group.members.length; i++) {
        let p = slot(group, i);
        if (group.game === "keep-away") {
            let destination = slot(group, target);
            if (i === chaser) p = {x: (group.width - size) / 2 + (destination.x - (group.width - size) / 2) * chaseU * .7,
                                  y: (group.height - size - 22) / 2 + (destination.y - (group.height - size - 22) / 2) * chaseU * .7};
            else { p.x += Math.sin(elapsed * 3 + i) * 8; p.y += Math.cos(elapsed * 3 + i) * 8; }
        }
        if (teaming) {
            let spread = phase < 71 ? size * .9 : size * .25;
            p = {x: group.width * .56 - size / 2 + (i % 2 ? spread : -spread),
                 y: group.height * .48 - size / 2 + (i < 2 ? -spread * .45 : spread * .45)};
        }
        poses.push({id: group.members[i].id,
            x: group.x + clamp(p.x, 0, group.width - size),
            y: group.y + clamp(p.y, 0, group.height - size - 22),
            size: size, effect: mode === "bonk" ? "bonk" : mode === "rally" ? "run" : group.game === "keep-away" ? "run" : group.game,
            frame: Math.floor(elapsed * 12) + i * 7,
            faceRight: p.x + size / 2 < group.width / 2,
            label: mode === "rally" ? "Team up!" : mode === "bonk" ? "TEAM BONK!" : group.game === "keep-away" ? (i === chaser ? "Get it!" : "Keep away!") : group.game === "catch" ? "Catch!" : "Square " + (i + 1)});
    }
    let order = group.game === "catch" ? [0, 1] : [0, 3, 1, 2];
    let leg = elapsed / (group.game === "catch" ? 1.8 : 1.1);
    let from = slot(group, order[Math.floor(leg) % order.length]);
    let to = slot(group, order[(Math.floor(leg) + 1) % order.length]);
    let u = leg - Math.floor(leg);
    let ball = {x: from.x + (to.x - from.x) * u + size / 2,
        y: from.y + (to.y - from.y) * u + size * .48 - Math.sin(Math.PI * u) * (group.game === "catch" ? group.height * .27 : size * .4),
        scale: group.game === "catch" ? 1 : .7 + .3 * Math.abs(Math.cos(Math.PI * u))};
    if (group.game === "keep-away") {
        let a = poses[source], b = poses[target];
        ball = {x: a.x - group.x + (b.x - a.x) * chaseU + size / 2,
                y: a.y - group.y + (b.y - a.y) * chaseU + size * .48 - Math.sin(Math.PI * chaseU) * 25, scale: 1};
    }
    return {mode: mode, actors: poses, ball: ball,
            chaser: group.members[chaser].id, loser: group.members[loser].id};
}

function approach(x, y, targetX, targetY, dt, speed) {
    let dx = targetX - x, dy = targetY - y, distance = Math.sqrt(dx * dx + dy * dy);
    let factor = distance > 0 ? Math.min(1, speed * Math.max(0, dt) / distance) : 0;
    return {x: x + dx * factor, y: y + dy * factor};
}
