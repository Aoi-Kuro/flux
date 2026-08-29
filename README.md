# Flux — Physics Practice Quiz Platform

Flux is a solo-built, vanilla-JS practice quiz platform for university physics
courses. It started as one HTML file with six random problems for a PHYS162
summer term and grew into a full multi-mode quiz app with theming, cross-device
stats, a moderated class forum with an AI participant, a searchable manual, and
offline support — no framework, no build step, no bundler.

This repo is the **framework**: one course's content (currently PHYS162) lives
inside it in a way that's designed to be swapped out wholesale, so the same
codebase can be redeployed for a different course (PHYS161, etc.) as its own
separate site with its own database. See [Deploying a new course](#deploying-a-new-course)
for exactly how.

> Live site: https://phys162.netlify.app

---

## Table of contents

- [How it's built](#how-its-built)
- [Project structure](#project-structure)
- [The multi-course architecture](#the-multi-course-architecture)
  - [`course/` — swap this wholesale](#course--swap-this-wholesale)
  - [`js/course-config.js` — the live switch](#jscourse-configjs--the-live-switch)
  - [What's still framework (shared)](#whats-still-framework-shared)
- [How each subsystem works](#how-each-subsystem-works)
- [Database (Supabase)](#database-supabase)
- [Edge functions](#edge-functions)
- [Running it locally](#running-it-locally)
- [Deploying a new course](#deploying-a-new-course)
- [Manual-swap items (can't be centralized)](#manual-swap-items-cant-be-centralized)
- [Versioning](#versioning)

---

## How it's built

- **No framework, no build step.** Plain HTML/CSS/JS, loaded as a stack of
  `<script>` tags in `index.html`, in a deliberate dependency order (see
  comments in `index.html` itself).
- **Supabase** for the forum, stats sync, and push notifications — Postgres +
  Row Level Security + Edge Functions (Deno/TypeScript), called directly from
  the browser with a public, RLS-restricted "publishable" key.
- **Netlify** for static hosting.
- **MathJax** (STIX Two font, vendored locally in `vendor/mathjax/`) for LaTeX
  rendering, with a persistent IndexedDB render cache for solve-all mode.
- **A service worker** (`sw.js`) for one narrow purpose: showing a real
  offline page instead of the browser's default "no internet" screen.

There's no `package.json`, no `npm install`, no dev server requirement beyond
"serve these static files" — see [Running it locally](#running-it-locally).

---

## Project structure

```
flux/
├── index.html              Main app shell — the quiz UI, landing screen,
│                            forum/stats/manual panels, and the full
│                            <script> load order (read its comments first)
├── offline.html             Fallback page shown by sw.js when there's no
│                            connection — a standalone page, not a route
├── sw.js                    Service worker: offline-page fallback + Web
│                            Push notification display/click handling
├── version.json              { "version": "X.Y.Z" } — read by
│                            quiz-engine.js's update-checker
│
├── course/                  ★ Everything specific to the currently-deployed
│   │                          course. See "The multi-course architecture".
│   ├── course.json          Reference-only doc: HTML header text (titles,
│   │                        OG/Twitter meta, eyebrow labels) for every
│   │                        course, for manual copy-paste at release time
│   ├── quizzes/
│   │   ├── quiz1.js .. quiz4.js   Problem banks (one file per quiz set)
│   │   └── quizzes.js       Registry wiring each quiz's name + enabled
│   │                        flag to its problem array (QUIZZES global)
│   ├── splashes.json        Minecraft-style main-menu splash text pool
│   ├── manual.json          User manual content (sections/subsections)
│   ├── offline-laws.json    Physics "law of the moment" shown on offline.html
│   ├── preview.png          Open Graph / Twitter card preview image
│   └── images/quiz_3/       Figure images referenced from quiz3.js problems
│
├── js/                       ★ Framework code — identical across every
│   │                          course deployment (nothing course-specific
│   │                          left here except manual-swap exceptions noted
│   │                          below).
│   ├── course-config.js      ⚡ Loads FIRST. Reads <head data-course="...">,
│   │                        exposes STORAGE_PREFIX / SUPABASE_URL /
│   │                        SUPABASE_PUBLISHABLE_KEY / PUSH_VAPID_PUBLIC_KEY
│   │                        for the active course. See below.
│   ├── banner-manager.js    Priority queue for the bottom notification
│   │                        banners (update / bug-report / theme-nudge)
│   ├── theme-colors.js      Reads live CSS custom properties into JS, so
│   │                        canvas/JS-drawn UI (confetti, π-day egg) stays
│   │                        in sync with the active color theme
│   ├── themes.js             Color theme picker, custom theme builder,
│   │                        day/night mode, one-time theme nudge
│   ├── splash.js             Fetches course/splashes.json, rolls a splash
│   │                        line on the landing screen
│   ├── easter.js             Pi Day / Pi Hour easter egg
│   ├── data/changelog.js    Changelog entries (shared across courses — this
│   │                        is the *platform's* dev history, not physics
│   │                        content, so it stays in js/ not course/)
│   ├── changelog.js          Changelog panel UI + a small "field lines"
│   │                        cursor toggle
│   ├── stats.js              Local attempt log (Random 6 mode), synced to
│   │                        a claimed forum identity
│   ├── stats-export.js       Stats screen export: CSV / TXT / Excel / PDF
│   ├── attempts-sync.js      Push/pull quiz attempts to/from Supabase
│   │                        (sync-quiz-attempts Edge Function)
│   ├── solve-all-sync.js    Cross-device sync for Solve-All progress
│   │                        (union-merge, not last-write-wins)
│   ├── math-cache.js        IndexedDB cache of pre-typeset MathJax output,
│   │                        keyed by a hash of each problem's LaTeX source
│   ├── math-render.js       Thin renderMathIn(el) wrapper around MathJax
│   ├── quiz-engine.js        The quiz engine itself: Practice mode, Solve
│   │                        Them All mode, Moodle-style number parsing,
│   │                        unit algebra/conversion, version-update banner
│   ├── fig-attribution.js   Tap-to-toggle (i) badges on figure images
│   ├── site-visits.js        Fires once per page load → record-visit
│   │                        Edge Function (feeds "Total visits" stat)
│   ├── forum.js              The class forum: read-only feed rendering,
│   │                        posting (via Edge Function, never direct
│   │                        .insert()), nicknames/PINs, replies, mentions,
│   │                        moderation UI, avatar caching
│   ├── push-notifications.js Web Push subscribe/unsubscribe UI for forum
│   │                        @mentions
│   └── manual.js              User manual browser (fetches course/manual.json)
│
├── css/
│   ├── style.css              Core UI: quiz cards, landing screen, theme
│   │                        presets (body[data-theme="x"] blocks), fonts
│   ├── forum.css              Forum screen (mirrors stats.css structurally)
│   ├── stats.css              Stats dashboard screen
│   └── manual.css             User manual screen
│
├── images/                   Framework-level images (NOT course-specific)
│   ├── gemini-logo.svg        Gemini bot avatar in the forum
│   └── offline/{dark,light}.png   offline.html illustration, both themes
│
├── favicon/                   Standard favicon set + site.webmanifest
│                            ("Flux" branding — shared across courses)
│
├── vendor/                    Vendored third-party libraries (no CDN
│                            dependency for these): MathJax, jsPDF, SheetJS,
│                            fonts
│
└── superbase/                 [sic — matches the folder name in this repo]
    │                          Everything for the Supabase backend. This
    │                          folder describes ONE Supabase project — the
    │                          currently-deployed course's. A new course
    │                          gets its own project built from the same
    │                          files, then course-specific edits (see
    │                          "Manual-swap items" below).
    ├── database.sql            Old context-only schema dump — superseded by
    │                          migrations/000, kept only for reference
    ├── migrations/              A single consolidated SQL file
    │                          (000_initial_schema_consolidated.sql) that
    │                          builds the entire database — tables, indexes,
    │                          view, functions, trigger, and RLS — in one
    │                          run against a fresh Supabase project
    ├── edge-functions/          Deno/TypeScript Edge Functions — see
    │                          "Edge functions" below for what each does
    └── schema-phys162.png      Reference screenshot of phys162's schema
```

---

## The multi-course architecture

**The model:** this repo is deployed once per course, each time as a
completely separate Netlify site + Supabase project + (eventually) separate
GitHub repo. Work on one course's copy, and when it's time to release a
different course, copy the `course/` folder's contents from that course,
hand-edit a small, well-marked set of header values, and redeploy. The
release step is manual and copy-based rather than templated at build time.

### `course/` — swap this wholesale

Everything in `course/` is real content that differs between courses:
problem banks, splash text, the manual, the offline-page law list, the OG
preview image, and course-specific images. To release a different course,
this entire folder's *contents* (quizzes, splashes, manual, offline-laws,
preview image, course images) get replaced with that course's versions.

`course/course.json` is the one file in there that's **not loaded by the
site at all** — nothing `fetch()`s or `<script>`s it. It exists purely as a
human-readable reference: it duplicates the exact title/meta/eyebrow text for
every course, so when you're releasing PHYS161 you can copy its block
straight into `index.html`/`offline.html` instead of re-deriving the strings
by hand. `index.html` marks the exact block this maps to with `COURSE HEADER
BLOCK` / `END COURSE HEADER BLOCK` comments.

### `js/course-config.js` — the live switch

This is the one framework file that's aware of multiple courses at once, and
it's the only place real secrets differ per course:

```js
const COURSES = {
  phys162: {
    storagePrefix: 'phys162',
    supabase: { url: '...', publishableKey: '...' },
    pushVapidPublicKey: '...',
  },
  phys161: {
    storagePrefix: 'phys161',
    supabase: { url: '', publishableKey: '' },   // filled in at release
    pushVapidPublicKey: '',
  },
};
```

It reads `document.head.dataset.course` — set via `<head data-course="phys162">`
at the very top of both `index.html` and `offline.html`, right inside the
COURSE HEADER BLOCK — and exposes three globals every other framework file
reads instead of hardcoding:

| Global | Used for |
|---|---|
| `STORAGE_PREFIX` | Every localStorage key and BroadcastChannel name across the app (`themes.js`, `splash.js`, `stats.js`, `forum.js`, `quiz-engine.js`, etc.) — was hardcoded `'phys162_...'` everywhere before this existed |
| `SUPABASE_URL` / `SUPABASE_PUBLISHABLE_KEY` | Every Supabase call (forum, stats sync, push) |
| `PUSH_VAPID_PUBLIC_KEY` | Web Push subscription (`push-notifications.js`) — each Supabase project has its own VAPID keypair |

It's loaded as the very first external `<script>` — before `banner-manager.js`
— because `themes.js`/`splash.js`/`easter.js` read `STORAGE_PREFIX` immediately
at load time, not lazily.

**To release a new course:** fill in that course's block in `COURSES`
(Supabase URL/key, VAPID public key), then flip the `data-course` attribute
on both HTML files' `<head>`.

### What's still framework (shared)

Everything in `js/` other than `course-config.js`, all of `css/`, the
generic images (`images/gemini-logo.svg`, `images/offline/`), and
`favicon/` are identical across every course deployment. `js/data/changelog.js`
also stays framework-side — it's the *platform's* build history, not physics
content, so it isn't course data.

---

## How each subsystem works

**Quiz engine** (`quiz-engine.js`) — Two modes: Practice (Random 6, one quiz
at a time or cumulative) and Solve Them All. Numeric answers are parsed with
Moodle-compatible rules (`parseMoodleNumber`) and checked with a unit-algebra
conversion layer, so `3000 m` and `3 km` both validate against an accepted
unit list per problem.

**Theming** (`themes.js` + `theme-colors.js` + CSS custom properties in
`style.css`) — Presets are CSS blocks (`body[data-theme="x"]`); the picker UI
and a custom-theme builder (auto-derives surface/border/muted/accent-dim from
just bg + text) live in JS. `theme-colors.js` reads the *live computed*
values of CSS variables so JS-drawn UI (canvas confetti, the π-day egg)
follows theme changes automatically instead of duplicating hex codes.

**Math rendering** (`math-render.js` + `math-cache.js`) — MathJax (STIX Two,
vendored) handles inline `$...$` / display `$$...$$` LaTeX. Solve-All mode
caches typeset output in IndexedDB keyed by a hash of each problem's source
text, so a repeat visit skips MathJax entirely for unchanged problems.

**Splash text** (`splash.js` + `course/splashes.json`) — Minecraft-style
rotating splash line under the site title. Each entry is `[text, condition,
mandatory]`; conditions gate on time-of-day/pi-time/etc.

**Stats** (`stats.js` + `stats-export.js` + `attempts-sync.js`) — Local
attempt log for Random 6 mode, exportable as CSV/TXT/Excel/PDF. Once a forum
identity is claimed, `attempts-sync.js` pushes/pulls attempts to Supabase
(`sync-quiz-attempts` Edge Function) — localStorage becomes a cache/queue,
not the source of truth.

**Solve-All sync** (`solve-all-sync.js`) — Same identity-linked sync model as
stats, but progress is a mutable per-problem status map, not an append-only
log, so cross-device merges are a union (keep whichever side "solved more"
per problem) instead of last-write-wins.

**Forum** (`forum.js`) — Read-only feed rendered client-side from
`forum_messages` via the RLS-restricted publishable key. All writes (post,
edit, flag, claim/drop nickname) go through Edge Functions, never a direct
`.insert()`. Includes nicknames + 5-digit PINs, `@mention` popups, replies,
DiceBear identicon avatars (cached), and an AI participant (`@gemini`,
OpenAI-moderated before posting, Gemini-generated) — see `post-message.ts`.

**Push notifications** (`push-notifications.js` + `sw.js`'s `push`/
`notificationclick` handlers) — Web Push subscription for forum @mentions.
Sending happens server-side in `post-message.ts`; the service worker only
displays the notification and routes a tap back into the right thread.

**Manual** (`manual.js` + `course/manual.json`) — Collapsible docs tree,
structurally mirrors the Forum/Stats screens. Content is plain HTML strings
with inline LaTeX, rendered through the same `renderMathIn()` helper.

**Offline support** (`sw.js` + `offline.html`) — Narrow-purpose service
worker: shows `offline.html` (with its own theme-matched illustration and a
random "law of the moment" from `course/offline-laws.json`) instead of the
browser's default offline screen. Does **not** cache the rest of the app for
full offline use.

**Changelog** (`js/changelog.js` + `js/data/changelog.js`) — Version bump
requires updating three places: `js/data/changelog.js`, `version.json`, and
`CURRENT_VERSION` in `quiz-engine.js` (the update-checker compares the
running page's version against `version.json` to show the update banner).

---

## Database (Supabase)

Schema is Postgres + Row Level Security. The entire database — every table,
index, view, function, trigger, and RLS policy — is built by running a
single file, `superbase/migrations/000_initial_schema_consolidated.sql`,
once against a fresh Supabase project. It was reconstructed and verified
directly against the live phys162 database (table defs, `pg_get_functiondef`
output, `pg_indexes`, `pg_policies`, `pg_tables`), not derived from
guesswork. `superbase/database.sql` is an old context-only dump kept for
reference; it's superseded by the migration file and was never meant to be
run directly.

Core tables (see `000_initial_schema_consolidated.sql` for exact columns):

| Table | Purpose |
|---|---|
| `forum_messages` | Forum posts — global or per-problem, with reply threading and edit/flag state |
| `identities` | Claimed nickname + PIN-hash identities |
| `identity_devices` | Links a device_id to a claimed identity (multi-device support) |
| `forum_flags` | Moderation flag queue |
| `site_visits` / `site_device_sightings` | Visit counters (record-visit.ts) |
| `device_bans` / `identity_bans` | Moderation bans |
| `quiz_attempts` / `quiz_attempts_counter` | Synced Random 6 attempt log + persistent counters |
| `solve_all_progress` | Per-identity, per-quiz solved-problem status map |
| `push_subscriptions` | Web Push subscriptions, keyed by device_id / identity_id |

---

## Edge functions

All deployed with auth mode **"publishable"**, **"Verify JWT with legacy
secret" OFF**, unless noted. Client code never calls Postgres directly for
writes — everything below is what stands between the public key and the
database.

| Function | Purpose | Secrets used |
|---|---|---|
| `post-message.ts` | Post a forum message — OpenAI moderation, then insert; handles `@gemini` replies and sends mention push notifications | `OPENAI_API_KEY`, `GEMINI_API_KEY`, `VAPID_PRIVATE_KEY`/`VAPID_PUBLIC_KEY`/`VAPID_SUBJECT` |
| `edit-message.ts` | Edit an existing message (own messages only) | `OPENAI_API_KEY` |
| `flag-message.ts` | Flag a message for moderation review | `GEMINI_API_KEY` |
| `claim-nickname.ts` | Claim a nickname + PIN (v2, multi-device identities) | `PIN_PEPPER` |
| `drop-nickname.ts` | Release a claimed nickname (v4, exit-only) | `PIN_PEPPER` |
| `check-ban.ts` | Check whether the calling device/identity is banned | — |
| `record-visit.ts` | Log a page visit for the site-visits counters | — |
| `sync-quiz-attempts.ts` | Push/pull local quiz attempts to/from the server | — |
| `delete-quiz-attempt.ts` | Delete a single synced attempt | — |
| `sync-solve-all.ts` | Pull + union-merge + push Solve-All progress | — |
| `save-push-subscription.ts` | Register/remove a Web Push subscription | — |

`PIN_PEPPER` is an extra secret input mixed into the PIN hash (on top of
normal salted hashing) so PIN hashes can't be brute-forced offline even with
full database access.

---

## Running it locally

No build step — this is a static site plus a remote Supabase backend.

```bash
# from the repo root
python3 -m http.server 8000
# or: npx serve .
```

Then open `http://localhost:8000`. The forum/stats/push features will talk to
whatever Supabase project is configured for the active course in
`js/course-config.js` — there's no local/mock backend.

Service worker note: `sw.js` only activates over `https://` or `localhost` —
a plain `file://` open won't register it, so use the local server above if
you need to test offline behavior.

---

## Deploying a new course

1. **Duplicate the repo** into a new one for the new course (this repo's
   design assumes each course is a fully separate repo/site, not a branch).
2. **Stand up a new Supabase project.** Run
   `superbase/migrations/000_initial_schema_consolidated.sql` once against
   it — this single file builds the entire database (tables, indexes, view,
   functions, trigger, RLS), verified to match the live phys162 project
   exactly.
3. **Deploy the Edge Functions** in `superbase/edge-functions/` to that
   project, same auth-mode settings noted in each file's header comment. Set
   its secrets: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `PIN_PEPPER`, and a fresh
   `VAPID_PRIVATE_KEY`/`VAPID_PUBLIC_KEY`/`VAPID_SUBJECT` triple (e.g. via
   `npx web-push generate-vapid-keys`).
4. **Edit `superbase/edge-functions/post-message.ts` by hand** in the new
   project's copy — `SITE_ORIGIN` and `GEMINI_SYSTEM_INSTRUCTIONS` are
   course-specific and can't be centralized (Edge Functions run in a separate
   Deno runtime with no access to `course-config.js`). Both are marked
   `⚠ COURSE-SPECIFIC — MANUAL EDIT AT RELEASE` in that file.
5. **Fill in `js/course-config.js`**: add (or fill in) that course's entry in
   `COURSES` — `storagePrefix`, `supabase.url`, `supabase.publishableKey`,
   `pushVapidPublicKey` (the public half from step 3).
6. **Replace the contents of `course/`** with the new course's quizzes,
   splashes, manual, offline-laws, preview image, and images.
7. **Edit the COURSE HEADER BLOCK** in both `index.html` and `offline.html`:
   change `data-course` on `<head>`, and paste in that course's values from
   `course/course.json` (title, OG/Twitter meta, the four eyebrow labels).
8. **Bump `sw.js`'s `CACHE_NAME`** to the new course's prefix by hand (see
   [Manual-swap items](#manual-swap-items-cant-be-centralized) — this is the
   one thing a service worker can't read from `data-course` itself).
9. **Deploy to Netlify** as a new site pointed at the new repo, with its own
   domain. Update `og:url` in `index.html` and `SITE_ORIGIN` in
   `post-message.ts` to match once you know it.

---

## Manual-swap items (can't be centralized)

A few things are genuinely course-specific but structurally can't be driven
by `js/course-config.js`, because they run somewhere that has no access to
it (a separate Deno runtime, or a DOM-less service worker scope). These are
called out with comments at each location so they're never a silent gap:

| Item | File | Why it can't be centralized |
|---|---|---|
| `CACHE_NAME` | `sw.js` | Service workers have no `document` — can't read the `data-course` attribute |
| `SITE_ORIGIN`, `GEMINI_SYSTEM_INSTRUCTIONS` | `superbase/edge-functions/post-message.ts` | Edge Functions deploy into their own Supabase-project Deno runtime, not the browser — can't import `course-config.js` |

---

## Versioning

Bump the version in **three places** on every release: `js/data/changelog.js`
(add an entry — indentation is derived automatically from major/minor/patch),
`version.json`, and `CURRENT_VERSION` in `js/quiz-engine.js`. The running
page polls `version.json` and shows the update banner (`banner-manager.js`)
when it drifts from `CURRENT_VERSION`.
