# Agent Activity prototype

From the repository root, run:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open http://127.0.0.1:8000/frontend/. Use Replay or scrub through the
synthetic run to inspect agent states and handoffs. The evaluations panel
reads the versioned case catalog and supports filtering by role.

This dependency-free prototype establishes the activity view before the
application frontend and live event API are implemented. See the
[agent design](../agents.md) for the intended live integration.

Run `python3 -m relay` before opening the page to load recorded events and
evaluation results from `relay-output/`. Select a dated edition to inspect
its handoffs or open its Markdown report. Each run uses a fresh output
directory. For an additional CLI run, pass `--output PATH`.
