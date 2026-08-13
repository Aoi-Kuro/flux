// ─── Quiz set registry ────────────────────────────────────────────────────────
// To add a new quiz:
//   1. Add its problem bank to js/data/quizN.js
//   2. Load that file in index.html (before quizzes.js)
//   3. Set enabled: true and point problems: to the array
const QUIZZES = [
  { name: "Electricity & Fields", problems: Quiz_1_Problems, enabled: true  },
  { name: "Circuits & Magnetism", problems: Quiz_2_Problems, enabled: true },
  { name: "Electromagnetism",       problems: Quiz_3_Problems, enabled: true },
  { name: "Light & Optics",       problems: Quiz_4_Problems, enabled: true },
];
