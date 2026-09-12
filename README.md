# private-service-access

I needed a place to keep my notes and stay organised, and Apple Notes wasn't
enough. I wanted it private, so I built it on my VPS behind WireGuard and nginx,
and learned a lot on the way.

Tailscale would have done the tunnel in ten minutes, but the parts it automates —
key distribution and NAT traversal — were the parts I wanted to understand more in depth and see if i can learn something new.

## Scheme

    laptop  10.8.0.2 ─┐
                      ├─ VPS 10.8.0.1
    phone   10.8.0.3 ─┘

## The problem I didn't expect

I brought down the Docker containers behind two other sites I host, and my
private checklist ended up served on the public internet.

Nginx matches a request in two steps: first the listen address, then the `Host`
header against `server_name`. With the other configs unlinked, nothing on
`0.0.0.0:80` matched any host, and nginx's rule for that case is to use the
default server for that listen address, that being the checklist.

I had assumed `listen 10.8.0.1:80` was enough. It makes that block unreachable
directly from outside, but it doesn't stop it being used as a fallback. Binding
constrains the block, not the files.

The fix was easy once I understood it:

    server {
        listen 0.0.0.0:80 default_server;
        return 444;
    }

`444` closes the connection with no response, and claiming the default slot
explicitly means nginx never has to guess.

## Port collision

`docker compose up` failed with `address already in use`. The Docker container
and the systemd service both wanted `127.0.0.1:8000`, and whichever started
first got it. Moved the app to 8001.

The real issue was that two systems were claiming host ports with nothing
recording which port belonged to what.

The API binds `127.0.0.1:8001` and nginx binds `10.8.0.1:80`. Neither socket
exists on the public interface, so there's nothing to reach even if a firewall
rule is wrong.

The leak incident is the limit of that: binding protects the socket and not the files.

## Firewall

    ufw allow 51820/udp
    ufw allow in on wg0

Interface-scoped rather than per-port, so anything on the tunnel works without a
new rule and the public interface stays closed.

## Files

| path | |
|---|---|
| `wireguard/` | server and client configs |
| `nginx/00-default-deny.conf` | the fix |
| `nginx/tracker.conf` | the tunnel-only vhost |
| `systemd/tracker.service` | the API unit |
| `verify.sh` | bindings, fallback and handshake age |

The app's HTML and CSS aren't here. The infrastructure is the point.
