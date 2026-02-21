# Suggested UI Add-ons

To further enhance the UI to match the "Perplexity" or "Premium" aesthetic, I recommend the following add-ons:

## 1. Icon Library
**Current State:** Using Emojis (e.g., ⚙️, 🕒).
**Recommendation:** **[Lucide Icons](https://lucide.dev/)** or **[Font Awesome](https://fontawesome.com/)**.
- **Why:** Vector icons scale perfectly, look professional, and offer a consistent style. Lucide is particularly popular for modern "clean" UIs.

## 2. Syntax Highlighting
**Current State:** Basic Markdown parsing via `marked.js`.
**Recommendation:** **[Highlight.js](https://highlightjs.org/)** or **[Prism.js](https://prismjs.com/)**.
- **Why:** Provides beautiful coloring for code blocks (Python, JS, HTML) returned by the agent, making it easier to read.

## 3. Animations
**Current State:** CSS Transitions.
**Recommendation:** **[AutoAnimate](https://auto-animate.formkit.com/)** (zero-config).
- **Why:** Adds smooth layout transitions when lists change (e.g., adding a new chat message or history item) without writing complex CSS.

## 4. Markdown Rendering
**Current State:** `marked.js`.
**Recommendation:** Keep `marked.js` but add **[DOMPurify](https://github.com/cure53/DOMPurify)**.
- **Why:** Security. Ensures that rendered HTML from the LLM is sanitized to prevent XSS attacks.
