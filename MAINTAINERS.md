# Maintainer Playbook

This repo is **Decap-only** for contributions. All changes should come in via Pull Requests.

## Review checklist (PRs)
### Data integrity (must)
- CI status check **validate** is green.
- IDs are stable and clean:
  - `id` uses `^[a-z0-9-]+$`
  - **filename matches id** (enforced by CI)
- References are valid:
  - `warband.unit_ids` refer to existing unit IDs
  - `unit.warband_ids` refer to existing warband IDs
- Source is present and specific:
  - Rulebook name
  - Page number(s) when available

### Quality (nice)
- Names match the source.
- Summary is short and factual (no long excerpts).
- No copyrighted PDFs or scans are uploaded.

## Common issues & how to handle
### Contributor changed an ID
- Ask them to revert the ID change.
- Explain: IDs are stable keys for references and URLs.
- If they need a new ID, create a **new entry** instead and deprecate the old one (optional, future).

### Missing/unclear source
- Request source details in the PR.
- If the source can’t be provided, close the PR politely.

### Conflicting changes
- Prefer the PR with a better source citation.
- If both are valid, merge the more complete one first, then rebase/refresh the other.

## Release / deploy notes
- GitHub Pages deploys automatically after merges to `main`.
- If Admin UI behaves oddly after changes:
  - hard refresh (Cmd+Shift+R)
  - verify `site/admin/config.yml` is present on Pages

## When to say “no”
- Uploads of rulebooks/PDFs/scans.
- Large copied text from books.
- Unverifiable changes without a source.
