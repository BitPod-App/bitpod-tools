# Taylor01 In-Repo Boundary

This subtree is the reserved future landing zone for portable Taylor01 content.

Current decision:

- keep Taylor01 in-repo for now
- avoid a separate repo until the boundary is more stable
- use this subtree to make future extraction cheaper

Subdirectories:

- `core/` for portable agent/runtime contracts and logic
- `policy/` for workspace and operating norms
- `adapters/` for third-party tool contracts and implementations

Do not migrate content here casually.

Only move artifacts when their Taylor01 ownership is clear enough to reduce coupling rather than create confusion.

