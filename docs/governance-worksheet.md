# Governance Retrospective - AI-Assisted Coding

## What I Shared With AI
| Item shared | Module | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|---|
| Task Tracker code | 2-5 | Low | Course toy-project application code with no credentials, tokens, or proprietary production logic in the inspected `app/` surface. | Paste only the smallest relevant file or function (for example one route plus its validator), not the whole tree, and exclude `.env` / secrets. | Confirm the repo was treated as course work only and that no real employer/client code was mixed into those pastes. |
| Test output and stack traces | 2-4 | Medium | Failure output often exposes local absolute paths, usernames, env-driven config, and internal call stacks even when the app itself is a toy project. | Paste the test name, assertion message, and a redacted snippet (replace home paths, tokens, connection strings, and emails with placeholders). | Whether any pastes included secrets, auth headers, real request payloads, or non-course data in the trace body. |
| Frontend code | 3 | Low | Course UI (`frontend/index.html` / components) talking to a local API base; inspected pattern is toy Kanban UI without production credentials. | Share one component and the exact behavior bug, not the full board file, and strip any non-local API URLs or keys if they ever appear. | Confirm no production API URLs, third-party keys, or real user-entered content were included in prompts. |
| Dockerfile and CI YAML | 4 | Low | Inspected `Dockerfile` and `.github/workflows/ci.yml` are generic build/test scaffolding with no registry passwords, deploy secrets, or production hostnames. | Share the failing stage/step only, with secrets referenced as `${{ secrets.NAME }}` placeholders rather than values. | Confirm you never pasted a different private org workflow that contained real tokens or protected environment names. |
| Any real external data I used by mistake | TODO | Unclassified | Risk depends entirely on whether real external/customer/user data was pasted; that fact is not stated in this worksheet. | If any real data was used: stop, rotate exposed secrets if needed, and replace future pastes with synthetic fixtures only. | Did you paste any real external data? If yes: what kind (PII, credentials, customer records, other), and in which module/chat? |

## Habit change order (High / Medium / High-potential only)
| Change first | Item | Risk | Why change this habit next |
|---|---|---|---|
| 1 | Any real external data I used by mistake | Unclassified → treat as High until ruled out | Highest blast radius: PII, credentials, or unauthorized data cannot be “unshared”; resolve the ambiguity and switch to synthetic fixtures before anything else. |
| 2 | Test output and stack traces | Medium | Only confirmed Medium habit; still routinely leaks paths, env, and payloads unless redaction becomes automatic. |

No other High items were classified. Low rows are deferred until the above habits stick.

## What I Received From AI
| Generated Thing | Module | Do I Understand It Line by Line? | Action |
|---|---|---|---|
| Backend models and validators | 2 | TODO | TODO |
| Frontend board and drag-and-drop logic | 3 | TODO | TODO |
| CI workflow | 4 | TODO | TODO |
| Dockerfile | 4 | TODO | TODO |
| Security findings and plans | 5 | TODO | TODO |
