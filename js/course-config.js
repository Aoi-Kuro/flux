// ── Course identity & per-course secrets ─────────────────────────────────────
// This site is deployed once per course (PHYS161, PHYS162, ...) as a
// completely separate repo/site each time. Everything that's IDENTICAL
// between deployments (framework code) stays here. Everything that
// DIFFERS is looked up below by the `data-course` attribute on <head> in
// index.html / offline.html — that attribute is the one thing you change
// by hand when spinning up a new course's copy of this repo.
//
// The human-readable copy-paste block (titles, meta tags, OG/Twitter text)
// lives in course/course.json — that file is NOT loaded by the site, it's
// just a reference doc for the manual header swap. THIS file is the one
// that's actually live: it must have a real entry for every course you
// deploy, including working Supabase credentials, or the site breaks.
//
// This script must load BEFORE anything that reads STORAGE_PREFIX,
// SUPABASE_URL, or SUPABASE_PUBLISHABLE_KEY — that means before
// banner-manager.js/themes.js/splash.js/easter.js, not just before forum.js.
// It's placed as the very first external <script> in index.html for that
// reason.

const COURSES = {
  phys162: {
    storagePrefix: 'phys162',
    supabase: {
      url: 'https://eammcjjsjyvmbjsloxpz.supabase.co',
      // Publishable key — safe to be public, RLS controls what it can
      // actually do (see the comment that used to live in
      // js/supabase-config.js). Never put the sb_secret_... key here.
      publishableKey: 'sb_publishable_NjZjecxc0iP1JnPSk5cJWQ_qllgCF7P',
    },
    // Public half of the VAPID keypair post-message.ts (in that project's
    // own superbase/edge-functions) signs pushes with. Public by design —
    // this is what identifies "a push claiming to be from this app", not
    // what lets anyone send one. Each Supabase project gets its own
    // keypair, so this is course-specific too.
    pushVapidPublicKey: 'BHEaaW9g9lqgGVa8cpwWaXq8Sy6vSdxYSJbhRpshv1G5WRExKk0NHqpU3oRPF8vetfrGzjmlV9T1u_xl18LszGY',
    // How big a "Random N" draw is, and — in cumulative mode — how many
    // of those N come from the previous quiz vs. the current one. Courses
    // can differ here (more/fewer problems per exam), so this isn't a
    // shared constant. cumulativePrevCount must be <= size; the remainder
    // (size - cumulativePrevCount) is drawn from the current quiz.
    quizSettings: {
      size: 6,
      cumulativePrevCount: 3,
    },
    // Row id in forum_messages shown pinned at the top of the forum
    // screen (see forum.js's renderForumPinnedBanner) — an ordinary
    // message, nothing server-side marks it special, this id is the only
    // thing that says "this one is the pinned one".
    pinnedMessageId: 336,
  },
  phys161: {
    storagePrefix: 'phys161',
    supabase: {
      // TODO(phys161 release): stand up the phys161 Supabase project
      // (schema + edge functions from superbase/), then fill these in.
      // Left blank on purpose — see below for what happens otherwise.
      url: 'https://ntlonovwrpspqncmejdm.supabase.co',
      publishableKey: 'sb_publishable_cj-dJARetQ3jv_1r3vqtKQ_kndImovt',
    },
    // TODO(phys161 release): generate a fresh VAPID keypair for the
    // phys161 project (web-push generate-vapid-keys or equivalent), put
    // the public half here and the private half in that project's own
    // post-message.ts secrets. Push subscriptions will just fail to
    // register with this blank until then — not fatal.
    pushVapidPublicKey: 'BLvjq8A2HzqQC58nNwFGINf7_iw1_K634_lYwJTqEJ5yW3XKcOjMNwbFTNat_KSEE_2S2VpU655evW1oGpXxGKM',
    // TODO(phys161 release): confirm these match phys161's actual exam
    // structure — defaulted to phys162's numbers (6 per quiz, 3 of those
    // from the previous quiz in cumulative mode) since nothing else was
    // specified yet.
    quizSettings: {
      size: 6,
      cumulativePrevCount: 3,
    },
    pinnedMessageId: 2,
  },
};

const ACTIVE_COURSE = (document.head.dataset.course || 'phys162').toLowerCase();
const _courseConfig = COURSES[ACTIVE_COURSE];

if (!_courseConfig) {
  console.error(
    `course-config.js: unknown data-course="${ACTIVE_COURSE}" on <head>. ` +
    `Known courses: ${Object.keys(COURSES).join(', ')}. Falling back to phys162.`
  );
}

const _active = _courseConfig || COURSES.phys162;

const STORAGE_PREFIX = _active.storagePrefix;
// Kept as SUPABASE_URL / SUPABASE_PUBLISHABLE_KEY (same names the old
// js/supabase-config.js used) so forum.js, attempts-sync.js,
// push-notifications.js etc. don't need to change at all.
const SUPABASE_URL = _active.supabase.url;
const SUPABASE_PUBLISHABLE_KEY = _active.supabase.publishableKey;
const PUSH_VAPID_PUBLIC_KEY = _active.pushVapidPublicKey;

// Read by quiz-engine.js's newQuiz() instead of hardcoding 6/3, so each
// course can have its own exam size without touching engine code.
// Falls back to the phys162 defaults (6, 3) if a course's entry omits
// quizSettings entirely, rather than silently producing NaN-length quizzes.
const _quizSettings = _active.quizSettings || COURSES.phys162.quizSettings;
const QUIZ_SIZE = _quizSettings.size;
const QUIZ_CUMULATIVE_PREV_COUNT = _quizSettings.cumulativePrevCount;

if (QUIZ_CUMULATIVE_PREV_COUNT > QUIZ_SIZE) {
  console.error(
    `course-config.js: quizSettings.cumulativePrevCount (${QUIZ_CUMULATIVE_PREV_COUNT}) ` +
    `exceeds quizSettings.size (${QUIZ_SIZE}) for "${ACTIVE_COURSE}" — ` +
    `cumulative mode will draw 0 problems from the current quiz. Fix the values in COURSES.${ACTIVE_COURSE}.quizSettings.`
  );
}

// Read by forum.js instead of hardcoding one row id, since each course's
// Supabase project has its own forum_messages table with its own welcome
// post at a different id. No sane fallback exists here (unlike
// quizSettings, there's no "default" pinned message across courses), so a
// course entry that omits this ends up with the banner just not showing —
// flagged loudly so that's never silent.
const FORUM_PINNED_MESSAGE_ID = _active.pinnedMessageId;
if (FORUM_PINNED_MESSAGE_ID == null) {
  console.error(
    `course-config.js: no pinnedMessageId set for "${ACTIVE_COURSE}" — ` +
    `the pinned forum banner will stay hidden until COURSES.${ACTIVE_COURSE}.pinnedMessageId is set.`
  );
}

if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
  // Not fatal — forum.js/attempts-sync.js/push-notifications.js all already
  // check `typeof SUPABASE_URL === 'undefined'` style guards and quietly
  // no-op without a client, they just won't have blank strings currently.
  // This just makes the "why isn't the forum loading" question answer
  // itself in devtools instead of failing silently.
  console.warn(
    `course-config.js: no Supabase credentials set for "${ACTIVE_COURSE}" — ` +
    `forum, stats sync, and push notifications will be disabled until ` +
    `COURSES.${ACTIVE_COURSE} in js/course-config.js is filled in.`
  );
}
