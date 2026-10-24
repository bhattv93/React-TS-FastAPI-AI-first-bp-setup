# Jira Bug Description Template

## Summary

{one line: what is wrong}

## Environment

- Env: local / dev / staging / prod
- Version / commit SHA:
- Browser / client (if UI):

## Steps to reproduce

1.
2.

## Expected vs actual

- Expected:
- Actual:

## Evidence

- `request_id` (from the `X-Request-ID` response header or the error toast):
- Logs or CloudWatch Logs Insights query link:
- Screenshot / HAR:

## Severity

S1 (prod down / data loss) · S2 (major feature broken, no workaround) · S3 (workaround exists) · S4 (cosmetic)

## Acceptance criteria for the fix

```gherkin
AC-1: Given {the reproduction state}
      When {the action}
      Then {the correct behaviour}
```

AC-1 becomes the regression test.
