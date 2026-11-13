# ADR-018: Studio UI kit: Tailwind CSS, Radix primitives, TanStack Query, generated API client
Status: Accepted    Date: 2026-11-13

## Context
The Studio (ADR-005) needs accessible dialogs, menus, tabs and focus handling to meet WCAG 2.2 AA (A-17), shared design tokens with the 2c prototypes (tokens.md), live data from the API with SSE updates, and a typed client generated from `openapi.yaml` (ADR-004). Requirements: R-61, R-40, NFR-08 (Studio accessibility part).

## Decision
- **Styling:** Tailwind CSS with the tokens from `docs/design/tokens.md` as CSS variables; no second styling system.
- **Primitives:** Radix UI primitives (unstyled, accessible) for dialog, popover, menu, tabs, tooltip, toggle; our own components on top in `web/components/`. Components are copied in-repo (shadcn/ui pattern), not a runtime theme dependency.
- **Data:** `openapi-typescript` generates types from `docs/contracts/openapi.yaml`; `openapi-fetch` is the client; TanStack Query caches queries and is invalidated by SSE events (ADR-005); since ADR-020 these arrive as AG-UI `CUSTOM` events.
- **Forms:** React Hook Form with validators generated from the same JSON Schema where possible (ADR-008).
- **Auth:** Auth.js generic OIDC provider (ADR-012).
- **Player:** `@remotion/player` with `media/scenes` (ADR-002, ADR-005).

## Alternatives
- **A full component library (MUI, Mantine):** heavier theming that fights the original token set.
- **CSS modules only:** fine, but slower to match 2c prototypes and no shared utility vocabulary for Cursor runs.
- **SWR instead of TanStack Query:** less control over SSE-driven invalidation.

## Consequences
- Easier: accessibility behaviour comes from Radix; prototypes and production share token names.
- Harder: copied components are ours to maintain; the `frontend.mdc` rule says to reuse them, never re-create.
