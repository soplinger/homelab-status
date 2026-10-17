# homelab-status

A small status page for a home server: memory, disk, load, uptime, and tmux sessions.
Standard library only, no install step.

Run the tests: `python3 -m unittest -q test_status`

Run the server: `python3 server.py 8080`, then open http://127.0.0.1:8080/ (localhost only).
The JSON is at `/api/status`.
