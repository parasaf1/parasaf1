# Engineering Pulse

A small, dependency-free Python CLI for generating local project status cards as SVG. This is an initial open-source prototype, separate from the profile's existing production renderers.

## What it does

- Renders 1–12 explicitly supplied project summaries.
- Supports neon and slate palettes.
- Escapes XML text and rejects unexpected JSON fields and invalid input.
- Reads only the JSON file specified by the operator. Makes no network requests, collects no telemetry, and never accesses private repositories.

## Run locally

Requires Python 3.10 or newer.

```sh
cd tools/engineering-pulse
python pulse.py example.json pulse.svg
python pulse.py example.json pulse-slate.svg --theme slate
python -m unittest -v
```

The example contains fictional sample projects clearly marked as examples. Supply your own approved public metadata with a top-level projects array; each item must contain name, status and milestone, with optional summary.

## Privacy and scope

The field allowlist is a schema check, not a secret detector. Review every input value before publication. This tool does not verify claims, infer product readiness or automatically collect activity. SVG text wrapping is approximate, and the current renderer is intended for short descriptions.

## License

[MIT](LICENSE) — applies to this tool only, not private products or other profile assets.

[Return to profile](../../README.md).
