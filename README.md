# Relay

Run the first offline research workflow with Python 3.11 or later. It uses
synthetic pricing snapshots and the standard library.

```sh
python3 -m relay
python3 -m http.server 8000 --bind 127.0.0.1
```

Open http://127.0.0.1:8000/frontend/ to inspect the three editions, recorded
handoffs, and evaluation statuses. The CLI writes Markdown, activity JSON,
and an eval report to the new `relay-output/` directory. Use
`python3 -m relay --output PATH` for another run without replacing editions.

The workflow scores the E13 baseline and a scoped E26 contract for the
three-day sequence. The remaining catalog cases are reported as not run.

See the [design specification](flagship-solution-and-agent-methodology.md),
[agent design](agents.md), and [evaluation harness](evals/README.md).
