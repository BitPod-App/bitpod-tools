# Taylor01 Portability Check Template v1

Use this block in relevant Linear issues and PRs.

```md
Taylor01 Portability Check

T01_LAYER: core | policy | adapter | bitpod-embedding | mixed
T01_SPECIFICITY: portable | bitpod-specific | mixed
T01_COUPLING: short note on what is still too coupled
T01_ACTION: keep-local | move-later | create-generic-version-now
```

## Example

```md
Taylor01 Portability Check

T01_LAYER: adapter
T01_SPECIFICITY: mixed
T01_COUPLING: workflow is generic, but current examples still assume Linear issue URLs and BitPod repo paths
T01_ACTION: create-generic-version-now
```

