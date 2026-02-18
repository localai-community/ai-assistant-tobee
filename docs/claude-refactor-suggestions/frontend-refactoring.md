# Frontend (Next.js) Refactoring Suggestions

## Critical

### 1. XSS Vulnerability via `dangerouslySetInnerHTML`

`MessageItem.tsx` and `DeepSeekReasoning.tsx` render content with `dangerouslySetInnerHTML`. The `formatContent` function does regex transforms but **no HTML sanitization**. If the LLM emits `<script>` or `<img onerror=...>`, it executes in the browser.

**Files affected:**
- `frontend-nextjs/app/components/MessageItem.tsx` (line ~141)
- `frontend-nextjs/app/components/DeepSeekReasoning.tsx` (line ~106)

**Recommendation:** Sanitize all HTML before rendering:
```bash
npm install dompurify @types/dompurify
```
```tsx
import DOMPurify from 'dompurify';

<div dangerouslySetInnerHTML={{
  __html: DOMPurify.sanitize(formatContent(message.content))
}} />
```

Alternatively, use a markdown renderer (`react-markdown`) instead of raw HTML injection.

---

### 2. Zero Test Infrastructure

No test files, no test libraries installed (no Jest, Vitest, Testing Library, Playwright), no `test` script in `package.json`.

**Recommendation:**
- Install Vitest + React Testing Library for unit/component tests
- Install Playwright for E2E tests
- Add `test` script to `package.json`
- Priority test targets: `useChat` hook (SSE streaming), `ChatInterface` (integration), API proxy routes

---

## High

### 3. Debug `console.log` Statements in Production Code

Extensive logging scattered throughout production code:
- `lib/api.ts` — logs every request URL and user setting updates
- `DeepSeekReasoning.tsx` — has a literal `"DeepSeekReasoning Debug:"` console.log block
- `useCurrentUser.ts` — logs every user save operation
- `Sidebar.tsx` — logs user deletion attempts and results

**Recommendation:** Remove all debug console.log statements. If runtime logging is needed, use a conditional logger that only outputs in development:
```typescript
const log = process.env.NODE_ENV === 'development' ? console.log : () => {};
```

---

### 4. `alert()` Used for Error Feedback

Blocking native `alert()` dialogs are used for errors in multiple components.

**Files affected:**
- `frontend-nextjs/app/components/ChatInput.tsx` (line ~75)
- `frontend-nextjs/app/components/Sidebar.tsx` (line ~283)
- `frontend-nextjs/app/components/FileUpload.tsx` (lines ~31, ~37)

**Recommendation:** Implement a toast/notification system (e.g., `react-hot-toast` or a custom component) and replace all `alert()` calls.

---

### 5. Magic Guest UUID Duplicated in 4+ Files

The string `'00000000-0000-0000-0000-000000000001'` is hardcoded in multiple files.

**Files affected:**
- `frontend-nextjs/lib/hooks/useCurrentUser.ts`
- `frontend-nextjs/lib/hooks/useChat.ts`
- `frontend-nextjs/app/components/ChatInterface.tsx`
- `frontend-nextjs/app/components/Sidebar.tsx`

**Recommendation:** Extract to a single constant:
```typescript
// lib/constants.ts
export const GUEST_USER_ID = '00000000-0000-0000-0000-000000000001';
```

---

### 6. Widespread `any` Type Usage

Despite `"strict": true` in tsconfig, `any` appears in critical locations:

| File | Location | Should Be |
|------|----------|-----------|
| `lib/api.ts` | `error: any` in interceptor | `unknown` with type guard |
| `lib/api.ts` | `handleApiError(error: any)` | `handleApiError(error: unknown)` |
| `Sidebar.tsx` | `onUpdateSetting value: any` | `UserSettings[keyof UserSettings]` |
| `ChatInterface.tsx` | `handleFileUploaded(document: any)` | `ChatDocument` |
| `lib/types.ts` | `SSEEvent.data: any` | Typed union of event data shapes |
| `lib/types.ts` | `context_data: any` | `Record<string, unknown>` |

**Recommendation:** Replace all `any` with proper types or `unknown` with type narrowing.

---

## Medium

### 7. Sidebar is a God Component (~680 lines)

Handles user management, conversation management, settings display, user creation, user deletion, and username validation all in one file with 13+ pieces of local state.

**Files affected:** `frontend-nextjs/app/components/Sidebar.tsx`

**Recommendation:** Decompose into:
- `UserManager` — user creation, deletion, switching
- `ConversationList` — conversation CRUD and selection
- `SettingsPanel` — AI model settings display/edit
- `Sidebar` — thin orchestrator that composes the above

---

### 8. Fragile Question-to-Message Matching

`MessageItem.tsx` tries to match questions to messages via content + time heuristics, with a final fallback to `questions[0]` — meaning if heuristics fail, it shows the first question ever asked regardless of relevance.

**Files affected:** `frontend-nextjs/app/components/MessageItem.tsx` (lines ~40-69)

**Recommendation:** Add a `question_id` foreign key to the message model in the backend, so the frontend can do a direct lookup instead of heuristic matching.

---

### 9. Axios + Fetch Redundancy

`lib/api.ts` uses axios for all REST calls, while `useChat.ts` uses native `fetch` for SSE streaming. The project ships the axios bundle for operations that `fetch` handles equally well.

**Recommendation:** Unify on native `fetch` and remove the axios dependency. Create a thin wrapper for common patterns (error handling, base URL, headers).

---

### 10. Dead Dark Mode CSS

`globals.css` defines a complete `[data-theme="dark"]` theme with full variable overrides, but no code ever sets `data-theme` on the HTML element. The dark mode CSS is entirely unused.

**Files affected:** `frontend-nextjs/app/styles/globals.css`

**Recommendation:** Either implement the dark mode toggle or remove the dead CSS to reduce stylesheet size and avoid confusion.

---

### 11. Duplicate CSS Selectors in Sidebar.module.css

Multiple selectors (`.inputGroup`, `.selectGroup`, `.textInput`, `.submitButton`, `.refreshButton`, etc.) appear **twice** in the ~760-line file. The latter definitions silently override the former.

**Files affected:** `frontend-nextjs/app/components/Sidebar.module.css`

**Recommendation:** Audit and deduplicate. Remove the first occurrence of each duplicated selector block.

---

### 12. Missing `'use client'` Directive

`DeleteConfirmationModal.tsx` uses event handlers and interactive features but lacks the `'use client'` directive. It works currently because it's imported from a client component, but this is technically incorrect and fragile.

**Files affected:** `frontend-nextjs/app/components/DeleteConfirmationModal.tsx`

**Recommendation:** Add `'use client'` at the top of the file.

---

## Low

### 13. Environment Variable Inconsistency

Most API routes use `NEXT_PUBLIC_BACKEND_URL`, but `upload/route.ts` and `health/route.ts` use `BACKEND_URL` (without the `NEXT_PUBLIC_` prefix). These could silently resolve to different values.

**Recommendation:** Standardize on `BACKEND_URL` for all server-side route handlers (they don't need `NEXT_PUBLIC_` prefix). Document this in `.env.local.example`.

---

### 14. `uploadProgress` State Never Used

`FileUpload.tsx` declares `const [uploadProgress, setUploadProgress] = useState(0)` but never updates or renders it.

**Files affected:** `frontend-nextjs/app/components/FileUpload.tsx`

**Recommendation:** Either implement upload progress tracking or remove the dead state.

---

### 15. `setTimeout` Without Cleanup

Several timeouts in `Sidebar.tsx` schedule `setTimeout(() => setUserIdChangeMessage(null), 3000)` but never store the timeout ID or call `clearTimeout` on unmount.

**Files affected:** `frontend-nextjs/app/components/Sidebar.tsx`

**Recommendation:** Store timeout IDs in a ref and clear them in a `useEffect` cleanup function.

---

### 16. Legacy Streamlit Frontend Still Present

The `frontend/` directory contains the entire old Streamlit app, including a committed `venv/` directory.

**Recommendation:** If deprecated, archive or remove the `frontend/` directory to reduce repo bloat. At minimum, add `frontend/venv/` to `.gitignore` and remove it from git history.
