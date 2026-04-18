# Vera Secret Boundary

Vera must have a separate runtime secret boundary.

## Vault
`Vera QA - Runtime`

## Hard rules
- no identities
- no break-glass
- no reuse of Taylor runtime secrets
- no reuse of Taylor identity surfaces

## Initial vault items
- `Vera QA - OpenAI API Key` -> `openai_api_key`
- `Vera QA - GitHub Token` -> `github_token`
- `Vera QA - Linear API Key` -> `linear_api_key`
