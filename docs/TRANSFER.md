# Moving `omnex-factory` into an organization

**Every step here is yours.** Nothing in this repository can create an
organization or transfer a repository, and this session has no tool that could.
What it can do is name the order, and say what breaks if a step is skipped —
which is the part that is easy to get wrong once and expensive to discover.

## What this is worth, measured

Before the ordering, the honest accounting. `RaveZona/omnex-factory` is
**public**, which means the features that would matter most here are already
reachable and an Enterprise adds none of them:

| already free on this repo | needs an organization |
|---|---|
| `actions/attest-build-provenance` | org-level rulesets across repos |
| required status checks on a branch | org secrets shared by several repos |
| secret scanning + push protection | required workflows |
| environment approval gates | teams, and the enterprise audit log |
| unlimited Actions minutes | one policy roof over the two private repos |

So the case for moving is a **portfolio** argument, not a capability one: one
ruleset and one `PYPI_API_TOKEN` covering this repo *and* `OMNEX` and
`omnex-system`, rather than three separately-configured islands. It is cheapest
now, while there is one repo and few external links.

**What could not be measured:** `docs.github.com` answers `403 to CONNECT` at
this environment's egress proxy, so per-plan entitlements as of today are
`UNKNOWN` and no figure for them is written here. The table above is about the
account model — an enterprise contains organizations, and an organization
contains repositories — not about a price list.

**The trial clock is not a reason.** A 31-day trial is economic pressure, and by
`CONSTITUTION.md` economic pressure may change **priority**, never readiness. If
the right moment is after the trial lapses, that is the right moment.

## Order, and what breaks if you skip

1. **Create an organization inside Omnex Technologies.**
   An enterprise contains organizations; it cannot hold a repository directly.
   `omnex-factory` is owned by the personal account `RaveZona`, so until an org
   exists there is nothing to transfer *into*.

2. **Grant the Claude GitHub App access to the new org.**
   *Skip it and this session loses the repository the moment it moves*, and every
   future session starts blind — the session's scope is a repository path, and
   the path changes. Do this **before** the transfer, not after.

3. **Transfer the repository.**
   Issues, pull requests, stars and releases travel with it. GitHub keeps a
   redirect from the old path, so existing git remotes keep working — but the
   canonical URL changes, and a redirect is a courtesy rather than a guarantee.

4. **Reconnect Vercel.**
   `omnex-ambassador` is wired to the old path and its preview deployments come
   through that integration. *Skip it and previews stop, quietly* — the checks
   simply stop appearing rather than turning red, which is the failure mode this
   repository keeps paying for.

5. **Update `[project.urls]` in `oss/citegate/pyproject.toml`.**
   They point at `github.com/RaveZona/omnex-factory`. `release_check.py` compares
   every `[project.urls]` entry against the git remote, so this turns from
   something to remember into something that fails the gate. Run
   `python scripts/release_check.py --target citegate` after the move; it will
   name the mismatch.

6. **Add a ruleset requiring status checks on `master`.**
   **The one that pays immediately.** Nothing today would have stopped `04b17e3`
   merging with CI red on all three interpreters — the whole gate architecture
   currently relies on somebody looking. Require at minimum:
   `Types, lint, tests (py3.11 / 3.12 / 3.13)` · `citegate (py3.11 / py3.13)` ·
   `Types, build, database tests` · `Golden suite regression gate`.

7. **Then, and only then**, evaluate moving `OMNEX` and `omnex-system` in. Those
   are private, so they are where Advanced Security and org policy actually buy
   something — but they are out of scope for this session by your own rule and
   nothing here has looked at them.

## Afterwards

- `state/claims.jsonl` carries `C-012`, "the Etsy listing API shape is readable
  from this environment", as `CONTRADICTED`. Nothing about the transfer changes
  that: it is a fact about the egress proxy, not about GitHub.
- Re-run the gate block from `CLAUDE.md`. `release_check.py` and
  `test_ci_contract.py` both read repository paths and will notice the move.
- If the redirect is ever removed, `git remote set-url origin <new path>`.

## What is deliberately absent

No step here is automated, and no script in this repository performs any of it.
Steps 1, 2, 3 and 6 are `CREDENTIAL`- and `DESTRUCTIVE`-class actions under
`policy.py`: irreversible or outward-facing, cleared by **no autonomy level
alone**, and requiring a durable authorization naming the class. A runbook is
the correct artifact for them. A script would not be.
