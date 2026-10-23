# Private TUI arena

[Back to the README](../README.md)

The arena is an optional feature for small, trusted groups. It is not required
for installation, GitHub progression, or pet care. Run the server command below
from the source checkout; player commands use the optional `omapet` launcher.

For an isolated Cloudflare Tunnel deployment, see [hosting and operations](HOSTING.md).

## Try a practice battle

```sh
omapet arena demo
```

Or open the TUI, press **a** for Arena, then **d** for offline practice. Choose
**1** Strike, **2** Guard, or **3** Feint. Your CPU rival commits its choice before
you pick yours; after a brief move-lock animation, the real arena rules resolve
the round. Press **n** for a new rival/rematch, or **q** / **Esc** to return.

Practice uses your saved name, character, and training traits. The rival gets the
same traits for a balanced preview. All players, HP, moves, and results exist only
in a disposable local arena; no network connection or invitation is needed. It
never changes your real pet, awards XP, spends energy, or replaces your saved
arena connection. Normal real-world care timers still pass while you practice.
The shared battle view also appears in the live arena. Older servers may not
report opponent characters; those use a generic robot portrait.

## Meet in the arena

One person hosts; friends connect to the same server over a trusted LAN/VPN or an
HTTPS reverse proxy. There is no hosted matchmaking service to sign up for.

```sh
# Host: generate and privately share an invitation. Keep these files out of git.
python3 -c 'import secrets; print(secrets.token_urlsafe(24))' > arena-invite.txt
chmod 600 arena-invite.txt
python3 -m omapet.arena --invite-file arena-invite.txt --host 127.0.0.1

# Every player: use the address exposed by your VPN or HTTPS proxy.
omapet arena connect http://127.0.0.1:8765
# The invitation is prompted without echo, rather than put in shell history.
omapet
```

For a trusted LAN/VPN, bind `--host` to that interface's address. Internet-facing
servers should sit behind HTTPS. The server bounds connections and applies basic
per-IP and global request limits; add edge controls for larger deployments.
The stdlib HTTP server is intended for small private groups. An invitation grants
registration access; treat it as a shared secret. HTTP sends arena tokens in cleartext,
so use HTTPS outside a trusted network. No GitHub credentials, logins, repository
names, contribution records, or home-care state are sent to the arena. A pet name
and four bounded traits are shared. The server stores hashed client tokens.

Press **a**, then **j** to queue. Two queued players automatically match. Each round,
choose **1** strike, **2** guard, or **3** feint; choices stay secret until both submit.
Strike beats feint, feint beats guard, guard beats strike. Strength powers strikes
and guards, agility powers feints, defense reduces damage, stamina adds battle HP.
Turns resolve simultaneously. A battle ends at zero HP or after 30 rounds. No
completed turn for five minutes expires a match; **l** leaves or concedes.

Completed matches grant 30 XP for a win, 10 for a loss or draw, for the first five
matches per UTC day. Each rewarded match costs 10 home energy. Concessions and
expired matches grant no XP. Repeated polling does not re-award XP. Players must
be healthy, awake, outside vacation, and have at least 20 energy to join through
the standard client.

The server owns turn order, hidden moves, HP, results, and match persistence.
Client-provided traits are clamped to 10–60, but they are **not cryptographically
verified**. Local saves and arena rewards can be edited. This is a friendly arena,
not an anti-cheat or ranked service. Server restarts retain players and matches;
change the invitation to prevent new registrations, and remove a player's record
from the stopped server's state to revoke its token.

## Collections, teams, and exchanges

For online 2v2, press **k** to open your collection, select a different pet from
the active one, and press **j**. Or run `omapet arena queue --team FIRST_ID SECOND_ID`.
Two-pet teams only match other two-pet teams. Each living pet attacks every round;
damage passes through the front pet before its teammate. The usual move controls
apply to the entire team. Each participating pet receives XP, with the five-match
daily reward limit shared by the household.

The collection also includes an adoption/trade board. **u** offers the selected
pet for free adoption, **t** offers it for any living pet in return, and **e** opens
the board. **g** refreshes and collects arrivals; **Enter** adopts or trades your
selected household pet for an offer. **x** cancels your own offer. Both sides keep
their pets' XP and trained traits. See the [collection guide](GUIDE.md#your-household-adoption-and-trading)
for commands, escrow behavior and recovery from interrupted transfers.

Update both arena server and clients for these features. Preserve `arena.json`
and each client's `arena-client.json`: they now also identify escrow owners,
open offers, transfer receipts, and pending deliveries. Restoring an old backup
can undo exchanges; coordinate server/client recovery together. As with battles,
pets originate from client-supplied saves and this is a trusted-group feature.
