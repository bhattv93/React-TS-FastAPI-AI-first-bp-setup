# Jira Story Description Template

> Paste into the Jira story description. Keep the headings exactly as written, because the
> `jira-story-to-spec` skill parses them.

## User story

As a **{role}**, I want **{capability}** so that **{benefit}**.

## Context

{Why now, links to designs or Confluence, related issues.}

## Acceptance criteria

```gherkin
AC-1: Given {precondition}
      When {action}
      Then {observable outcome}

AC-2: Given …
      When …
      Then …
```

## Non-functional requirements

- NFR-1: {performance / security / accessibility requirement, measurable}

## Impact

- API change: yes/no. If yes, which endpoints and the request/response shape sketch.
- DB change: yes/no. If yes, which tables/columns.
- UI change: yes/no. If yes, the design link.

## Out of scope

- {explicitly excluded items}

## Open questions

- {must be empty before the story is Ready}
