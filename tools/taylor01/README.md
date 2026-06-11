# Taylor01 In-Repo Boundary

This subtree is the reserved future landing zone for portable Taylor01 content.

Current decision:

- keep Taylor01 in-repo for now
- avoid a separate repo until the boundary is more stable
- use this subtree to make future extraction cheaper
- use Hermes-first runtime coordination for active Taylor01/Vera agent workflow
- treat OpenClaw as closure/cleanup history only, not a fallback runtime

Subdirectories:

- `core/` for portable agent/runtime contracts and logic
- `policy/` for workspace and operating norms
- `adapters/` for third-party tool contracts and implementations

Active example:

- `core/agents/vera/` is the canonical portable home for Vera's first-class QA agent definition
- `adapters/hermes/` contains the Hermes-first runtime coordination contract
- `adapters/hermes/vera/` contains the Hermes-first Vera execution-path contract
- `adapters/openai/vera/` contains current bridge execution adapters
- `adapters/openclaw/vera/` contains historical OpenClaw closure/mapping residue only

Do not migrate content here casually.

Only move artifacts when their Taylor01 ownership is clear enough to reduce coupling rather than create confusion.
