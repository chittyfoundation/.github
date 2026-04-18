# ChittyFoundation

> Making proof as frictionless as speech

Independent non-profit stewarding **ChittyChain** trust infrastructure and **ChittyDNA** human rights standards for the AI age. Separate from commercial applications by design — like IETF for protocols, but for trust and verification.

## What We Build

**Trust Infrastructure** — ChittyChain provides foundational, blockchain-backed trust infrastructure: immutable audit trails, cryptographic verification, and governance standards that serve the ecosystem without commercial bias.

**Human x AI Rights** — ChittyDNA establishes standards for attribution, compensation, and worker protection as AI transforms every industry. The world's first Human x AI Rights framework.

## Core Projects

| Project | Purpose |
|---------|---------|
| [ChittyChain](https://github.com/chittyfoundation/chittychain) | Trust infrastructure blockchain — consensus, verification, immutability |
| [ChittyID](https://github.com/chittyfoundation/chittyid) | Universal identity management with P/L/T/E/A entity ontology |
| [ChittyChronicle](https://github.com/chittyfoundation/chittychronicle) | Event logging and audit trail system |
| [ChittyOps](https://github.com/chittyfoundation/chittyops) | Operational governance primitives and cross-organizational territories |
| [ChittyAdvocate](https://github.com/chittyfoundation/chittyadvocate) | Doctrine narrative bootstrap for AI substrate alignment |

## Governance

ChittyFoundation operates as a 501(c)(3) non-profit with structural independence:

- **Independent Board** — academics, protocol architects, legal/ethics experts, community representatives
- **Endowment-funded** — no commercial P&L pressure, no equity investments, no data monetization
- **RFC-style standards** — 30-day public comment, 3+ expert reviews, reference implementation required
- **Transparent operations** — all decisions publicly auditable, quarterly reports, annual third-party audits

## Standards

All repositories follow the ChittyCanon governance framework:

- Compliance triad: CHARTER.md (contract) + CHITTY.md (architecture) + CLAUDE.md (dev guide)
- Canonical entity types: Person, Location, Thing, Event, Authority (P/L/T/E/A)
- Fractal trinity layout: identity / authority / connectivity / scopes (see template below)
- Reusable CI via [centralized workflows](.github/workflows/)
- Claude-powered code review + governance checks

## Starter Template (BINDING for new repos)

**[chittyseed-fractal](https://github.com/chittyfoundation/chittyseed-fractal)** — every new ChittyOS repo MUST start from this template. Click "Use this template" on the GitHub repo page, or run:

```bash
gh repo create CHITTYFOUNDATION/<your-service> --template chittyfoundation/chittyseed-fractal --public
```

The template encodes the fractal trinity layout (identity / authority / connectivity), provides the standard `scope.json` manifest, CHARTER/CHITTY/CLAUDE templates, package.json with `validate:fractal` + `certify` scripts, and a CI workflow that gates merges on fractal-layout compliance.

Validation contract: `chittycanon://core/services/chittyschema#meta/fractal-layout`

## Get Involved

- **Explore**: Browse repositories and read their CHARTER.md for scope
- **Contribute**: See individual CONTRIBUTING.md files
- **Discuss**: Open issues or discussions in any repository

---

[foundation.thechitty.com](https://foundation.thechitty.com)
