# My AI Playbook

## When I reach for AI first

- Boilerplate and config syntax I don't write often — CI YAML, Dockerfile stages, `.dockerignore` patterns. I used AI to draft the first pass of `ci.yml` and the `Dockerfile`, then checked the details myself (Python version, non-root user, HEALTHCHECK).
- Cross-checking docs against code. Having AI scan `AGENTS.md`-style files for things like "does the README's storage claim match `app/storage.py`" is faster than me reading every module by hand, as long as I re-verify the specific claim it flags.
- A first-pass review of a diff before I merge it — catching things like a stray `continue-on-error` or a missing `HEALTHCHECK` that I might skim past on my own.
- Explaining an error message or unfamiliar library behavior when I'm stuck and just need a plausible starting hypothesis to test.

## When I do not reach for AI first

- Anything touching `app/` or `frontend/` business logic — the status-transition rules, validation, or the missing `DELETE` route. Those are the parts of this project I'm actually being graded on understanding, so I read the code myself before asking AI to weigh in.
- Deciding whether a security finding is actually exploitable. AI can point me at `/test/reset` and note it's "guarded," but I don't trust that until I hit the endpoint myself with and without `APP_ENV=test` set and see the real response.
- Anything involving `.env` or real data. I don't paste env values or task data into a prompt to "help AI understand the bug" — I describe the shape of the problem instead.
- The first time I'm learning a concept for a course, not just shipping it. If the point of an exercise is for me to understand Docker healthchecks or CI shortcuts, I try it myself first and use AI to check my work, not to hand me the answer.

## My non-negotiables

- Never paste `.env` contents, tokens, credentials, or real task/customer data into an AI tool — `.env.example` only.
- Never accept a suggestion that weakens a check to make something pass — the `continue-on-error: true` suggestion for CI is the clearest example; I rejected it because a pipeline that can't fail isn't testing anything.
- Never claim I verified something because AI said it works. If AI says "the endpoint is guarded" or "tests pass," I run it myself before it goes in `docs/`.
- Never let AI touch `app/` or `frontend/` without me reading the exact diff line by line first — those are the protected paths for a reason.

## My review rules

- I read the diff before I read AI's summary of the diff, not after — otherwise I just end up agreeing with whatever it emphasized.
- For every AI comment on a review, I grade it Useful / Noise / Wrong and write down *why*, not just the label. If I can't state a reason, that's usually a sign I didn't actually check it.
- Security findings get one extra step: file evidence. "This might be a problem" isn't a finding until I can point to the actual file and line, like `requirements.txt` missing `pytest`/`httpx` even though CI depends on them.
- If an AI finding turns out to rest on a wrong assumption about the codebase — like guessing at a JSON storage file path when the real implementation is in-memory — I mark it a false positive and move on instead of forcing it to be right.

## What I am still figuring out

- Where the line is between "AI drafted this and I verified it" and "AI drafted this and I mostly trusted it" — on a good day I can tell the difference, on a rushed day I'm less sure I'm being honest with myself about which one happened.
- How much of AI's *reasoning* I should record versus just its conclusions. Right now I mostly log grades and short reasons; I don't know yet if that's enough evidence for a teammate to trust my judgment later, or just enough to pass a rubric.
- What my rule should be for team settings where not everyone reviews AI output as carefully as I try to — one careful reviewer on a team doesn't make the whole PR trustworthy.

## Decision Card


| Situation                  | My one rule                                                                                                             |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| New feature                | Don't let AI scope-creep it — if AI's plan touches files the task didn't ask about, cut it back before reading further. |
| Code review                | Grade every AI comment Useful/Noise/Wrong with a reason before acting on any of them.                                   |
| Debugging                  | Ask AI for hypotheses, not fixes — I still have to reproduce the bug myself.                                            |
| Infrastructure (CI/Docker) | If a suggestion makes a check easier to pass instead of harder to fail, reject it.                                      |
| Never-paste                | `.env` values, tokens, credentials, and real task/customer data — no exceptions.                                        |
| One rule (overall)         | If I can't explain why AI's suggestion is right, it doesn't go in the repo.                                             |


