# Priority Summary

At-a-glance priority matrix across the whole project.

## Priority Matrix

| Priority | Backend | Frontend |
|----------|---------|----------|
| **P0 — Critical** | Auth system for all endpoints | XSS sanitization (`dangerouslySetInnerHTML`) |
| | Exception detail leaking to clients | Test infrastructure setup |
| | Test coverage (zero tests exist) | |
| **P1 — High** | CORS/secret key security config | Remove debug `console.log` statements |
| | Remove redundant requirements files | Replace `alert()` with toast notifications |
| | Migrate Pydantic v1 → v2 patterns | Extract `GUEST_USER_ID` constant |
| | | Replace `any` types with proper types |
| **P2 — Medium** | Dependency injection for ChatService | Decompose Sidebar god component |
| | Consolidate config access (Settings obj) | Unify HTTP client (drop axios) |
| | API prefix consistency (reasoning router) | Clean dead dark mode CSS |
| | Deprecated SQLAlchemy patterns | Fix duplicate CSS selectors |
| | Consolidate ORM model files | Fix question-to-message matching |
| | | Add missing `'use client'` directive |
| **P3 — Low** | Deprecated `@app.on_event()` | Env variable naming consistency |
| | Module-level side effects | Remove dead `uploadProgress` state |
| | Duplicate logger assignment | `setTimeout` cleanup on unmount |
| | Docker fixes (version, .dockerignore, user) | Remove legacy Streamlit frontend |

## Suggested Execution Order

1. **Security first** — Fix XSS, auth, exception leaking, secret key
2. **Foundation** — Set up test infrastructure for both backend and frontend
3. **Cleanup** — Remove dead code, debug logs, duplicate files
4. **Modernize** — Pydantic v2, SQLAlchemy 2.x, complete uv migration
5. **Architecture** — DI, component decomposition, config consolidation
6. **Polish** — Docker improvements, CSS cleanup, dark mode implementation
