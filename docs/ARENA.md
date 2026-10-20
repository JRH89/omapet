# Private TUI arena

[Back to the README](../README.md)

The arena is an optional feature for small, trusted groups. It is not required
for installation, GitHub progression, or pet care. Run the server command below
from the source checkout; player commands use the optional `omapet` launcher.

For an isolated Cloudflare Tunnel deployment, see [hosting and operations](HOSTING.md).

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
