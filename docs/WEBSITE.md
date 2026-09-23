# Project website draft

The website draft is maintained in `site/`. It contains a landing page, project
notes, an SVG mark, four protocol figures, local CSS, and a small
evidence-policy teaching example. All participant examples are generic. No
individual artist names, account identifiers, or profile URLs belong in public
content. The demo uses fictional inputs and does not verify signatures or
accept payments.

The editorial sources are the accepted
[Bitcoin-rooted identity decision](../adr/0005-bitcoin-rooted-self-custodial-identity.md),
[the vision](00-vision.md),
[the roadmap](13-roadmap.md),
[the architecture](01-architecture.md),
[the event and album identity profiles](../specs/music-object-schema.md),
[the cryptographic profile](../specs/cryptographic-profile.md),
[the public proof-package profile](../specs/proof-package-schema.md), and
[the paid-use proposal](16-artist-authorized-use-payments.md).
The flow, framework, stack, and pipeline figures follow
[the protocol flow](diagrams/02-end-to-end-protocol-flow.md),
[the protocol framework](diagrams/09-protocol-framework.md),
[the software stack](diagrams/05-software-stack-architecture.md), and
[the release pipeline](diagrams/06-deployment-pipeline.md).
Update the public summaries and those figures when the sources change. Keep
private source paths and maintainer notes out of the public pages.

## Preview and validation

```bash
python3 scripts/build_site.py
python3 -m http.server 8080 --bind 127.0.0.1 --directory .site-dist
```

Open `http://127.0.0.1:8080`. The export has an explicit eleven-file allowlist;
only those curated files are included. The script checks page structure,
local links/anchors, project-relative asset URLs, and obvious private paths
or artist-profile URLs. Manual review still checks text and any indirect
identifiers. `robots.txt` and page metadata request no indexing while this is
a draft; they do not provide access control.

## GitHub Pages

The Sites deployment is publicly accessible under the recorded default policy.
GitHub Pages remains a separate release route: keep `PAGES_ENABLED` unset or
false unless that route is explicitly enabled. Do not create a public source
repository or change the protocol repository's visibility as part of Sites
publication.

The workflow `.github/workflows/pages.yml` builds the public bundle on relevant
pushes and pull requests. Deployment requires Pages configured for GitHub
Actions and repository variable `PAGES_ENABLED=true`. The artifact includes
only `.site-dist/`; the repository root, internal documentation, and memory
state are never used as the Pages artifact.

At the setup check on 2026-09-23, `ffwd-org/o2a-protocol` was private and the
organization used GitHub Free. GitHub Pages does not support private source
repositories on that plan. A separate public repository containing just the
curated site is a possible publishing destination; changing the protocol
repository's visibility is not necessary for that approach. Alternatively,
an eligible paid organization plan can serve Pages from the private source.
[GitHub Pages availability and workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

The source repository has multiple push URLs configured for `origin`. Any
publishing command must name the intended repository explicitly rather than
using an unqualified `git push`.

## Public live draft with Sites

The draft is hosted at
[O2A Protocol — Public Draft](https://o2a-protocol.edwinkestler.chatgpt.site).
Its default access policy is `public`: anyone with the URL may retrieve the
curated site without signing in. This public audience decision applies to the
Sites deployment, not to repository visibility or GitHub Pages configuration.
The `noindex` page metadata and `robots.txt` remain draft-indexing requests;
they are not access control.

`.openai/hosting.json` records the existing Sites project ID. Reuse it; never
create a replacement site for an update. Only the eleven curated website files
and this hosting manifest belong in the Sites source snapshot. Protocol
documents, GitHub history, Palimnex data, and credentials are excluded.

The Sites snapshot has its own Git repository under ignored
`.sites-work/source/`. This keeps deployment commits separate from unfinished
protocol documentation. The configured static directory is `dist`.

To prepare an update locally:

```bash
python3 scripts/build_site.py
python3 - <<'PY'
from pathlib import Path
import shutil
stage = Path('.sites-work/source')
stage.mkdir(parents=True, exist_ok=True)
target = stage / 'dist'
assert not target.is_symlink()
if target.exists():
    shutil.rmtree(target)
shutil.copytree('.site-dist', target)
(stage / '.openai').mkdir(exist_ok=True)
shutil.copyfile('.openai/hosting.json', stage / '.openai/hosting.json')
PY
```

Review and commit only that snapshot, then use a short-lived Sites repository
write credential to push its exact HEAD to the Sites-provided remote and
branch. Keep credentials in process memory, never in files or remote URLs. A
successful source push does not by itself save a Sites version or deploy it.
Build the archive from that same pushed commit:

```bash
git -C .sites-work/source archive --format=tar.gz -o ../o2a-site.tar.gz HEAD
git -C .sites-work/source rev-parse HEAD
```

Read the current Sites access policy immediately before release. The expected
policy is `public`. If it has drifted, restore `public` under this recorded
default and re-read the policy before deployment. Audience changes remain
explicit Sites operations; a source push or deployment must not silently
change access.

Use the Sites `save_site_version` operation with the existing project ID, full
commit SHA, and absolute archive path, then deploy that exact saved version
with `deploy_site_version`. Confirm a successful production deployment and
re-check the public audience. Verify anonymous requests can retrieve both pages
and static assets with HTTP 200, and inspect the live content rather than
treating an access response as deployment proof.

Deployment evidence and validation results are recorded below; refresh them
after each deployment rather than assuming an older test proves a new version.

### Version 1 historical validation — 2026-09-23

This is evidence for version 1 at its validation time, not proof of the current
deployment or access policy. Re-check both after every access or deployment
change.

- Sites deployment completed successfully; owner-only access policy revision 1.
- Source commit: `b4d5124b237ae223632de55c0f5c2c82e53f2984` in the isolated
  Sites snapshot repository, not the protocol repository.
- Archive SHA-256:
  `1d1b0a943cd389c2864ac016065613c5b1cdef5a6cf1fc5ffe05d6a4eb39e423`.
- Signed-out requests to `/`, `/guide.html`, and `/assets/site.js` returned
  HTTP 401 without website content.
- Authorized Chromium checks loaded both pages at 1440, 768, 390, and 320 px
  with HTTP 200 and no horizontal overflow.
- The sample policy, challenge override, and keyboard toggle checks passed;
  no browser console or page errors were observed.
- Seven-file export validation and Git whitespace checks passed for version 1.

### Version 2 validation — 2026-09-23

- Before release, the live access policy had drifted to `public` at revision 4.
  With explicit authorization, it was restored to `custom` owner-only access
  at revision 5, with no other viewers, editors, groups, or external visitors.
- Sites production deployment completed successfully at the existing private
  review URL as saved version 2.
- Source commit: `ce6212b8e532069bd7b809ea54dd0bfc06206b2a` in the isolated
  Sites snapshot repository, not the protocol repository.
- Archive SHA-256:
  `6f4f45354e1757eb7117ca3cdb0e94a200c2d9a655bc78796178a8f26c5dceac`.
- Signed-out requests to `/`, `/guide.html`, and `/assets/site.js` returned
  HTTP 401 without the curated website content.
- Authorized requests loaded both pages and all three protocol figures with
  HTTP 200. The home page contained the protocol section and figure links, and
  the guide contained the release-pipeline update.
- Ten-file export validation and Git whitespace checks passed. Browser viewport
  and interaction checks were not rerun for version 2.

This validates the version 2 website bundle, deployment, and access gate within
the checks above. It does not validate an O2A protocol implementation, payment
system, or RGB smart contract.

### Version 3 validation — 2026-09-23

- Sites production deployment completed successfully at the existing private
  review URL as saved version 3.
- The access policy remained `custom` owner-only at revision 5: one owner, no
  other viewers or editors, no groups, and no external visitors.
- Source commit: `14fa1e6b551cc9a281c19fbe72cf3aa290f83330` in the isolated
  Sites snapshot repository, not the protocol repository.
- Archive SHA-256:
  `e441bcbf4242a27881f867b26fbb55b077646f57e25e414f99228076699fbe4b`.
- Signed-out requests to `/`, `/guide.html`, and
  `/assets/protocol-stack.svg` returned HTTP 401.
- Authorized requests loaded both pages and all three protocol figures with
  HTTP 200 after following the site's canonical redirect.
- The live homepage, guide, and stack figure contained the new decentralized,
  Bitcoin-rooted, self-custodial identity language.
- Ten-file export validation, SVG XML parsing, relative Markdown-link checks,
  and Git whitespace checks passed. Browser viewport and interaction checks
  were not rerun for version 3.

This validates the version 3 website bundle, deployment, and access gate within
the checks above. It does not validate an O2A wallet, Bitcoin/RGB protocol
implementation, payment system, or mainnet release.

### Version 4 validation — 2026-09-23

- Sites production deployment completed successfully at the existing private
  review URL as saved version 4.
- The access policy remained `custom` owner-only at revision 5: one owner, no
  other viewers or editors, no groups, and no external visitors.
- Source commit: `62a245a79a868e3347c627ec6bfbc305d73d9cd7` in the isolated
  Sites snapshot repository, not the protocol repository.
- Archive SHA-256:
  `1390e2bad205912e611e92412d42f7bd183c94c160c9380776c059b4d11c6d57`.
- Signed-out requests to `/`, `/guide.html`, and
  `/assets/protocol-stack.svg` returned HTTP 401.
- Authorized requests loaded both pages and all three protocol figures with
  HTTP 200 after following the site's canonical redirect.
- The live guide contained the immutable-root/controller distinction, public
  content-addressed proof-package rule, open-source intent and license gate,
  and the corrected specification-status heading.
- Ten-file export validation, SVG XML parsing, relative Markdown-link checks,
  JSON validation, Git whitespace checks, and all 21 Palimnex evaluation cases
  passed. Browser viewport and interaction checks were not rerun for version 4.

This validates the version 4 website bundle, deployment, and access gate within
the checks above. It does not validate an O2A wallet, proof-package
implementation, RGB contract, payment system, or mainnet release.

### Version 5 validation — 2026-09-23

- Before release, the live access policy had drifted to `public` at revision 6.
  Under the private-live authorization, it was restored to `custom` owner-only
  access at revision 7: one owner, no other viewers or editors, no groups, and
  no external visitors.
- Sites production deployment completed successfully at the existing private
  review URL as saved version 5.
- Source commit: `1e593c8e01135c698eb84cefa535387d9069ea63` in the isolated
  Sites snapshot repository, not the protocol repository.
- Archive SHA-256:
  `92725e8b8af86c7c28105c53678695cecce729a4cb251f7b3b42276a1965fae7`.
- Signed-out requests to `/`, `/guide.html`, and
  `/assets/protocol-framework.svg` returned HTTP 401.
- Authorized requests loaded both pages and the flow, framework, stack, and
  pipeline figures with HTTP 200 after following the site's canonical redirect.
- Live content checks found the new framework, sequential release gates, and
  four-figure protocol section.
- Eleven-file export validation, SVG XML parsing, local visual rendering,
  relative Markdown-link checks, Git whitespace checks, and all 21 Palimnex
  evaluation cases passed.

This validates the version 5 website bundle, deployment, and access gate within
the checks above. It does not validate an O2A wallet, proof-package
implementation, RGB contract, payment system, or mainnet release.

### Version 6 validation — 2026-09-23

- Sites production deployment completed successfully at the existing private
  review URL as saved version 6.
- The access policy remained `custom` owner-only at revision 7: one owner, no
  other viewers or editors, no groups, and no external visitors.
- Source commit: `67299f1d9725ee189939890055cb6a6b1763fbff` in the isolated
  Sites snapshot repository, not the protocol repository.
- Archive SHA-256:
  `c74aae3aae1df8328c245f8fc0f75f263c54766e22522b308a01b01392509f09`.
- Signed-out requests to `/`, `/guide.html`, and
  `/assets/protocol-pipeline.svg` returned HTTP 401.
- Authorized requests loaded the homepage, guide, and pipeline figure with
  HTTP 200 after following the site's canonical redirect.
- Live content checks found the Apache License 2.0 decision in the guide and
  the accepted Apache-2.0 gate in the pipeline figure.
- Eleven-file export validation, SVG XML parsing and visual rendering,
  canonical-license comparison, relative Markdown-link checks, Git whitespace
  checks, and all 21 Palimnex evaluation cases passed.

This validates the version 6 website bundle, deployment, and access gate within
the checks above. It does not validate an O2A wallet, proof-package
implementation, RGB contract, payment system, or mainnet release.
