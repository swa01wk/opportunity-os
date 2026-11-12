# ADR-005: Next.js (React, TypeScript) for the Studio
Status: Accepted    Date: 2026-11-12

## Context
The Studio needs structured review surfaces, side-by-side evidence and narration, scene cards with a playhead, and in-browser previews that match the renderer (R-61, R-17, R-28, R-31). Desktop only (A-26).

## Decision
- Next.js App Router, React, TypeScript, in `web/`.
- The Studio embeds the **Remotion Player** with the same `media/scenes` components the renderer uses, so a scene preview is the same code as the render (ADR-002).
- All data comes from the FastAPI API using a client generated from `docs/contracts/openapi.yaml`. Next.js route handlers are used only for the auth callback; no domain logic in `web/`.
- Live progress via Server-Sent Events from `GET /v1/projects/{id}/events`.

## Alternatives
- **Vite SPA (React):** simpler, but Next.js gives auth middleware and server-side session handling with less custom code.
- **Server-rendered Python templates:** cannot share Remotion components for previews.

## Consequences
- Easier: one component library for preview and render.
- Harder: two TypeScript consumers (`web`, `media/scenes`) must use the generated types, not their own (ADR-008).
