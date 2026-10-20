# Hosting an invite-only arena

The arena is for small, trusted groups. It has no verified rankings or protection
against edited client stats. A Cloudflare Tunnel supplies public HTTPS without
publishing an application port on the host. The origin and tunnel run as separate
non-root containers in one dedicated Compose project.

## Deployment layout

Use a new directory, for example `~/services/omapet-arena`:

```text
compose.yml                 integrations/arena/compose.yml
.env                        pinned Python and cloudflared image digests
cloudflared.yml             one arena hostname and a final http_status:404 rule
src/omapet/                 Python source only
src/integrations/arena/Dockerfile
secrets/invite              random shared invitation, mode 0600
secrets/tunnel.json         credentials for this arena tunnel only, mode 0600
state/arena.json            persistent game state, mode 0600
backups/                    fourteen daily state snapshots
backup.py                   integrations/arena/backup.py
```

Make the deployment, state, secret, and backup directories private (0700). The
Compose example runs as UID/GID 1000; adapt both services and file ownership if
your deployment user has different IDs. Never place secrets in the build context.
Resolve and pin the image digests in `.env`:

```text
PYTHON_IMAGE=python@sha256:YOUR_VERIFIED_DIGEST
CLOUDFLARED_IMAGE=cloudflare/cloudflared@sha256:YOUR_VERIFIED_DIGEST
```

## A separate tunnel

Inspect existing tunnel services, containers, configs, and DNS before making
changes. Create a **new named tunnel**; do not reinstall cloudflared's system
service, replace its default config/certificate, restart other projects, overwrite
DNS, or change other tunnels' ingress rules.

Cloudflared's login certificate is zone-specific for DNS operations. Check that
its zone matches the desired domain before routing DNS: a certificate for another
zone can append that zone to the supplied hostname. If necessary, log in with a
separate HOME directory and pass its certificate using `--origincert`.

Example config (substitute a newly created UUID and your hostname):

```yaml
tunnel: NEW_ARENA_TUNNEL_UUID
credentials-file: /run/secrets/tunnel.json
metrics: 127.0.0.1:19265
ingress:
  - hostname: arena.example.com
    service: http://127.0.0.1:18765
    originRequest:
      connectTimeout: 5s
  - service: http_status:404
```

Copy only that tunnel's credentials into `secrets/tunnel.json`. Route only the
new hostname, without overwrite flags. The app binds to loopback **inside the
container network namespace**. The dedicated tunnel shares that namespace; neither
container publishes a host port or joins another application's network.

## Start and verify

```sh
docker compose up -d --build
docker compose ps
curl --fail https://arena.example.com/healthz
```

The app bounds concurrent connections to 16, caps request bodies at 8 KiB, uses
five-second connection timeouts, and throttles per-client traffic and registration.
It trusts `CF-Connecting-IP` only with the explicit `--trust-cloudflare` switch,
which requires a loopback bind. Do not publish that origin port or insert another
proxy that accepts untrusted client headers unchanged. Containers have read-only
roots, dropped capabilities, no-new-privileges, resource limits, bounded logs, and
pinned images. Invitations and client bearer tokens must remain private. The
account-wide Cloudflare login certificate is never mounted into the containers.

These controls support a private pilot; the stdlib server and JSON storage are
not intended for large public matchmaking. Cloudflare edge rate/WAF rules can add
another layer if the service grows. A shared invitation authorizes registration;
revocation/account recovery and verified stats remain future work.

Test two-player matchmaking, hidden moves, match completion, invalid invitations,
restart persistence, and restored backups before sharing the invitation. Compare
existing tunnel config hashes and service/container start times afterward.

## Operations

Run commands from this deployment's directory, always specifying its own Compose
file/project if working elsewhere. Do not run broad Docker cleanup commands.

```sh
docker compose ps
docker compose logs --tail 100 arena tunnel
docker compose restart arena     # Compose restarts its dependent tunnel too
python3 backup.py "$PWD"
```

Schedule the backup script daily using a dedicated user systemd timer. Keep
backups private and test a restore in a temporary directory first. To restore the
live game, stop this project's containers, back up the current state, install the
chosen valid snapshot as `state/arena.json` with owner 1000:1000 and mode 0600,
then start this project again. Daily snapshots remain on the host; add an off-host
backup separately for protection against loss of the server.

To rotate the invitation, replace only `secrets/invite` securely and recreate this
project's app and tunnel (`docker compose up -d --force-recreate`). Existing players
retain their bearer tokens; invitation rotation only affects new registrations.
To revoke a player, stop the arena and remove its identity from the state, then
restart. Do not edit a live state file.

Shutdown/rollback: `docker compose down` in this directory stops only this project.
It preserves bind-mounted state and secrets. DNS and the named tunnel can then be
removed separately by their exact IDs, after checking they belong to the arena.
