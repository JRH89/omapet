.pragma library

function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }

// Stable IDs keep a polling refresh from reshuffling games or restarting animations.
function roster(pets) {
    return pets.filter(p => p.roaming && p.can_roam !== false).slice().sort((a, b) => a.id.localeCompare(b.id));
}

function arrange(pets, screenWidth, screenHeight) {
    let members = roster(pets), chunks = [], groups = [];
    while (members.length >= 4) chunks.push(members.splice(0, 4));
    while (members.length >= 2) chunks.push(members.splice(0, 2));
    // An odd pet continues its usual free roaming instead of being stranded in a game.
    let columns = Math.max(1, Math.min(chunks.length, Math.floor(screenWidth / 310)));
    let rows = Math.max(1, Math.ceil(chunks.length / columns));
    let width = Math.min(430, Math.max(120, (screenWidth - 24) / columns));
    let height = Math.min(330, Math.max(120, (screenHeight - 64) / rows));
    let size = Math.min(144, Math.max(54, Math.min(width / 2.6, height / 2.5)));
    for (let i = 0; i < chunks.length; i++) {
        let col = i % columns, row = Math.floor(i / columns);
        groups.push({id: chunks[i].map(p => p.id).join("/"), members: chunks[i],
            game: chunks[i].length === 4 ? "four-square" : "catch", index: i, size: size,
            x: Math.max(0, (screenWidth - columns * width) / 2 + col * width),
            y: Math.max(0, (screenHeight - 40 - rows * height) / 2 + row * height),
            width: width, height: height});
    }
    return groups;
}

function slot(group, index) {
    let pad = 12, size = group.size;
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
    for (let i = 0; i < group.members.length; i++) {
        let p = slot(group, i);
        if (teaming) {
            let spread = phase < 71 ? size * .9 : size * .25;
            p = {x: group.width * .56 - size / 2 + (i % 2 ? spread : -spread),
                 y: group.height * .48 - size / 2 + (i < 2 ? -spread * .45 : spread * .45)};
        }
        poses.push({id: group.members[i].id,
            x: group.x + clamp(p.x, 0, group.width - size),
            y: group.y + clamp(p.y, 0, group.height - size - 22),
            size: size, effect: mode === "bonk" ? "bonk" : mode === "rally" ? "run" : group.game,
            frame: Math.floor(elapsed * 12) + i * 7,
            faceRight: p.x + size / 2 < group.width / 2,
            label: mode === "rally" ? "Team up!" : mode === "bonk" ? "TEAM BONK!" : group.game === "catch" ? "Catch!" : "Square " + (i + 1)});
    }
    let order = group.game === "catch" ? [0, 1] : [0, 3, 1, 2];
    let leg = elapsed / (group.game === "catch" ? 1.8 : 1.1);
    let from = slot(group, order[Math.floor(leg) % order.length]);
    let to = slot(group, order[(Math.floor(leg) + 1) % order.length]);
    let u = leg - Math.floor(leg);
    let ball = {x: from.x + (to.x - from.x) * u + size / 2,
        y: from.y + (to.y - from.y) * u + size * .48 - Math.sin(Math.PI * u) * (group.game === "catch" ? group.height * .27 : size * .4),
        scale: group.game === "catch" ? 1 : .7 + .3 * Math.abs(Math.cos(Math.PI * u))};
    return {mode: mode, actors: poses, ball: ball};
}

function approach(x, y, targetX, targetY, dt, speed) {
    let dx = targetX - x, dy = targetY - y, distance = Math.sqrt(dx * dx + dy * dy);
    let factor = distance > 0 ? Math.min(1, speed * Math.max(0, dt) / distance) : 0;
    return {x: x + dx * factor, y: y + dy * factor};
}
