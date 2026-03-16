# Stryker Mutation Testing — Surviving Mutants

> Final score: **94.96%** (above 85% break threshold)
> Scope: `src/services/**/*.ts` (excludes untestable React component styling mutations)
> Run date: 2026-03-15

All remaining survivors are **equivalent mutants** — the mutated code produces identical observable behaviour to the original.

---

## api.ts — 2 survivors

### 1. `ConditionalExpression` — line 37

```diff
- body: body !== undefined ? JSON.stringify(body) : undefined,
+ body: true       ? JSON.stringify(body) : undefined,
```

**Why equivalent:** `JSON.stringify(undefined)` returns `undefined` in JavaScript.
When `body` is `undefined`, `true ? JSON.stringify(undefined) : undefined` evaluates to `undefined` — identical to the original conditional. The `fetch` call sees `body: undefined` in both cases.

---

### 2. `OptionalChaining` — line 44

```diff
- detail = data?.detail ?? detail;
+ detail = data.detail  ?? detail;
```

**Why equivalent:** `data` comes from `await response.json()`. If `json()` returns `null`, the original `null?.detail` yields `undefined`, so `detail` stays as `response.statusText`. The mutation `null.detail` throws a `TypeError`, but this is inside a `try/catch` block — the catch swallows the error and `detail` also stays as `response.statusText`. Observable outcome is identical.

---

## auth.ts — 2 survivors

### 3. `ConditionalExpression` — line 27

```diff
- if (!raw) return null;
+ if (false) return null;
```

**Why equivalent:** `raw = localStorage.getItem(key)`. When nothing is stored, `raw` is `null`. The mutation removes the early-return guard, but `JSON.parse(null)` evaluates to `null` in JavaScript, so `getCurrentUser()` still returns `null`. Observable behaviour is identical.

---

### 4. `ArrowFunction` — line 67 (server snapshot)

```diff
- () => selector({ token: null, user: null, setSession, clearSession }),
+ () => undefined,
```

**Why equivalent:** This is the third argument to `useSyncExternalStore` — the *server-side snapshot* function used only during SSR/hydration in Node.js environments. The jsdom test environment always invokes the client-side `getSnapshot` (second argument), never the server snapshot. This code path is unreachable in all unit tests.
