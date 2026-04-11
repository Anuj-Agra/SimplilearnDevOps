---
name: html-prototype-builder
description: >
  Build production-quality HTML prototype pages locally as a Figma replacement.
  Accepts an existing page screenshot/image or HTML file to extract and match the
  visual style exactly, then generates new pages or components in the same design
  language. Asks the user targeted questions before building. Use when asked:
  'create an HTML page', 'prototype this screen', 'build a UI mockup', 'design
  this page locally', 'replace Figma', 'HTML wireframe', 'recreate this screen',
  'match this design', 'build from screenshot', 'clone this page style', 'local
  prototype', 'no Figma', 'HTML mockup', 'design without Figma', 'build from
  image', 'generate HTML from design', 'create login page', 'create dashboard',
  'create form', 'build UI', 'make a prototype'. Produces self-contained HTML files
  that open directly in any browser with no build step. Extracts design tokens
  (colours, typography, spacing, components) from existing pages or images and
  reuses them across all generated pages.
---
# HTML Prototype Builder

Build pixel-quality HTML prototypes locally — no Figma, no build tools, no
server required. Opens in a browser. Fully editable. Design-system consistent.

---

## Agent Modes

Detect which mode from the user's message:

| Input provided | Mode |
|---|---|
| Screenshot or image of an existing page | **[CLONE MODE]** — extract style, match exactly |
| Existing `.html` file uploaded | **[EXTEND MODE]** — read tokens, build new page in same style |
| Description only (no existing design) | **[CREATE MODE]** — ask questions, then design from scratch |
| Screenshot + "build a new page like this" | **[EXTEND MODE]** — extract from image, apply to new page |

---

## Phase 1 — EXTRACT (Clone & Extend modes)

When an image or HTML file is provided, extract the complete design system
**before asking any questions or writing any code**.

### From an Image/Screenshot

Analyse the image and extract:

**Colours** (scan every visible UI element)
```
Primary action colour:  [hex] — buttons, links, highlights
Secondary colour:       [hex] — secondary buttons, badges
Background:             [hex] — page background
Surface:                [hex] — cards, panels, modals
Border:                 [hex] — dividers, input borders
Text — primary:         [hex] — headings, body
Text — secondary:       [hex] — labels, captions, placeholders
Text — inverse:         [hex] — text on dark backgrounds
Success:                [hex] — confirmations, positive states
Warning:                [hex] — caution states
Error:                  [hex] — validation, destructive actions
```

**Typography**
```
Heading font:    [name or description — e.g. "bold sans-serif, tight tracking"]
Body font:       [name or description — e.g. "regular weight, generous line height"]
Heading sizes:   H1=[size] H2=[size] H3=[size]
Body size:       [size]
Weight usage:    [e.g. "700 for headings, 500 for labels, 400 for body"]
Letter spacing:  [e.g. "tight on headings, normal on body"]
```

**Spacing & Layout**
```
Base unit:       [e.g. 4px or 8px — infer from visible gaps]
Section padding: [e.g. 48px vertical, 24px horizontal]
Card padding:    [e.g. 24px]
Component gap:   [e.g. 16px between form fields]
Border radius:   [e.g. 8px cards, 4px inputs, 999px pills]
Max content width: [e.g. 1200px]
Grid columns:    [e.g. 12-column, or sidebar + main]
```

**Component Patterns**
```
Buttons:    [describe: filled / outlined / ghost, radius, padding, shadow]
Inputs:     [describe: border style, focus state, label position — floating/above/inline]
Cards:      [describe: shadow depth, border vs borderless, hover state]
Navigation: [describe: top bar / sidebar / tabs, active state]
Tables:     [describe: striped / bordered / hover rows, header style]
Badges:     [describe: filled / outlined, shape, size]
Icons:      [describe: style — line / solid / duotone, size, colour usage]
```

**Tone & Style**
```
Overall feel:   [e.g. "corporate and formal", "modern SaaS", "financial services navy"]
Dark/Light:     [Light / Dark / System]
Density:        [Compact / Comfortable / Spacious]
Shadow depth:   [Flat / Subtle / Elevated / Dramatic]
```

### From an HTML File

```bash
# Parse existing HTML for design tokens
grep -o "color:[^;]*;\|background[^;]*;\|font-family:[^;]*;\|font-size:[^;]*;\|\
border-radius:[^;]*;\|padding:[^;]*;\|margin:[^;]*;\|box-shadow:[^;]*;" \
  <uploaded_file>.html | sort | uniq -c | sort -rn | head -40

# Extract CSS variables if present
grep -o "--[a-zA-Z-]*:[^;]*;" <uploaded_file>.html | sort | uniq

# Extract font imports
grep -o "fonts\.googleapis\.com[^\"]*\|fonts\.gstatic\.com[^\"]*\|\
@import.*font[^;]*" <uploaded_file>.html
```

Extract all CSS custom properties (`--*`) and recurring values into a
**Design Token Set** — this becomes the single source of truth for
all pages generated in this session.

---

## Phase 2 — QUESTION (All modes — run before writing any code)

Never build without asking these questions first. Group them into a
single message — do not ask one at a time.

### For Clone/Extend Mode (image or HTML provided)

```
I've analysed your existing design. Here's what I extracted:

🎨 DESIGN SYSTEM DETECTED
  Primary colour: [hex]  Background: [hex]  Text: [hex]
  Font: [description]    Spacing unit: [size]   Radius: [size]
  Style: [description — e.g. "Financial services, dark navy, formal"]

✅ I'll match this exactly for the new page.

Before I build, a few quick questions:

1. WHAT to build:
   What is this new page for? (e.g. "Order detail page", "User profile", "Settings")

2. CONTENT to include:
   What sections or components does it need?
   (e.g. "Header, summary card, data table, action buttons")
   Or describe the user's goal: "A manager reviewing and approving an order"

3. DATA to show:
   What information should appear on the page?
   (e.g. "Customer name, order items, total, status, approval buttons")

4. USER ACTIONS available:
   What can the user do on this page?
   (e.g. "Approve, Reject, Download PDF, Edit")

5. NAVIGATION:
   How does the user get here, and where do they go next?
   (e.g. "Came from the orders list, 'Approve' goes back to list")

6. DEVICE target:
   Desktop only / Mobile responsive / Both?

7. LINKED PAGES:
   Should buttons/links navigate to other prototype pages,
   or are they non-functional placeholders?

Answer as many as you can — I'll make sensible assumptions for anything
you skip.
```

### For Create Mode (description only, no existing design)

```
Before I design this page, I need to understand the context:

1. WHAT IS THIS FOR:
   - System/product name?
   - Who uses this page? (Role — e.g. "Customer Service Agent", "Manager")
   - What is the user trying to accomplish?

2. VISUAL STYLE — pick the one that fits best, or describe your own:
   □ Professional & Corporate  (structured, formal, trust-building)
   □ Modern SaaS               (clean, spacious, sidebar nav)
   □ Financial Services        (navy/dark, data-dense, precise)
   □ Consumer App              (friendly, colourful, accessible)
   □ Internal Tool / Admin     (functional, dense, utilitarian)
   □ Dashboard / Analytics     (data-forward, charts, KPI cards)
   □ Other: [describe]

3. COLOUR PREFERENCE:
   □ I have brand colours: [paste hex codes]
   □ Use dark/navy theme
   □ Use light/white theme
   □ You decide — match the style I described

4. CONTENT:
   What sections, data, or components should appear?
   (Be as specific or vague as you like — I'll fill gaps)

5. USER ACTIONS:
   What can the user do on this page?

6. PAGES NEEDED:
   Is this one page, or should I build multiple linked pages
   as a clickable prototype?

7. TECHNICAL:
   □ Pure HTML/CSS (no frameworks — works offline)
   □ Include Tailwind CSS (CDN)
   □ Include Bootstrap (CDN)
   □ Include a charting library (Chart.js)
```

---

## Phase 3 — BUILD

After receiving answers, generate the HTML. Read
`/mnt/skills/public/frontend-design/SKILL.md` for aesthetic principles.

### Design Token CSS Block (always first)

Every generated page starts with a comprehensive CSS custom properties block.
When in Clone/Extend mode, populate from the extracted values.
When in Create mode, define a coherent design system from scratch.

```html
<style>
  /* ── Design Tokens ─────────────────────────────────────── */
  :root {
    /* Brand colours */
    --color-primary:        [hex];   /* primary action */
    --color-primary-hover:  [hex];   /* darker shade */
    --color-primary-subtle: [hex];   /* 10% opacity background */
    --color-secondary:      [hex];
    --color-accent:         [hex];

    /* Semantic colours */
    --color-success:        [hex];
    --color-success-subtle: [hex];
    --color-warning:        [hex];
    --color-warning-subtle: [hex];
    --color-error:          [hex];
    --color-error-subtle:   [hex];

    /* Backgrounds */
    --color-bg:             [hex];   /* page background */
    --color-surface:        [hex];   /* cards, panels */
    --color-surface-raised: [hex];   /* modals, popovers */
    --color-border:         [hex];   /* dividers, outlines */
    --color-border-focus:   [hex];   /* focus ring */

    /* Text */
    --color-text:           [hex];   /* primary body */
    --color-text-secondary: [hex];   /* labels, captions */
    --color-text-disabled:  [hex];   /* inactive states */
    --color-text-inverse:   [hex];   /* on dark surfaces */
    --color-text-link:      [hex];   /* hyperlinks */

    /* Typography */
    --font-heading:  '[font name]', [fallback stack];
    --font-body:     '[font name]', [fallback stack];
    --font-mono:     '[font name]', monospace;

    --text-xs:   0.75rem;   /* 12px */
    --text-sm:   0.875rem;  /* 14px */
    --text-base: 1rem;      /* 16px */
    --text-lg:   1.125rem;  /* 18px */
    --text-xl:   1.25rem;   /* 20px */
    --text-2xl:  1.5rem;    /* 24px */
    --text-3xl:  1.875rem;  /* 30px */
    --text-4xl:  2.25rem;   /* 36px */

    --weight-normal:   400;
    --weight-medium:   500;
    --weight-semibold: 600;
    --weight-bold:     700;

    --leading-tight:  1.2;
    --leading-normal: 1.5;
    --leading-loose:  1.75;

    /* Spacing (8px base unit) */
    --space-1:  0.25rem;  /* 4px  */
    --space-2:  0.5rem;   /* 8px  */
    --space-3:  0.75rem;  /* 12px */
    --space-4:  1rem;     /* 16px */
    --space-5:  1.25rem;  /* 20px */
    --space-6:  1.5rem;   /* 24px */
    --space-8:  2rem;     /* 32px */
    --space-10: 2.5rem;   /* 40px */
    --space-12: 3rem;     /* 48px */
    --space-16: 4rem;     /* 64px */

    /* Border radius */
    --radius-sm:   4px;
    --radius-md:   8px;
    --radius-lg:   12px;
    --radius-xl:   16px;
    --radius-full: 9999px;

    /* Shadows */
    --shadow-sm:  0 1px 2px rgba(0,0,0,0.05);
    --shadow-md:  0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
    --shadow-lg:  0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
    --shadow-xl:  0 20px 25px rgba(0,0,0,0.15), 0 10px 10px rgba(0,0,0,0.04);

    /* Layout */
    --max-width:       1280px;
    --sidebar-width:   240px;
    --nav-height:      64px;
    --content-padding: var(--space-8);
  }
</style>
```

### Component Library (generate once, reuse across pages)

```html
<!-- ── REUSABLE COMPONENTS ─────────────────────────────── -->

<!-- Buttons -->
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-danger">Destructive</button>

<!-- Status badges -->
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Rejected</span>
<span class="badge badge-neutral">Draft</span>

<!-- Form inputs -->
<div class="field">
  <label class="field-label">Field Label <span class="required">*</span></label>
  <input type="text" class="field-input" placeholder="Enter value">
  <span class="field-hint">Helper text goes here</span>
</div>

<!-- Cards -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <div class="card-actions"><!-- action buttons --></div>
  </div>
  <div class="card-body"><!-- content --></div>
  <div class="card-footer"><!-- footer --></div>
</div>

<!-- Data table -->
<div class="table-wrapper">
  <table class="data-table">
    <thead><tr><th>Column</th></tr></thead>
    <tbody><tr><td>Cell</td></tr></tbody>
  </table>
</div>

<!-- Alert / notification -->
<div class="alert alert-success">
  <div class="alert-icon">✓</div>
  <div class="alert-content">
    <strong class="alert-title">Success</strong>
    <p class="alert-body">Message text here.</p>
  </div>
</div>
```

### Page Structure Templates

Read `references/page-templates.md` for full HTML for each page type.

Available templates:
- `sidebar-nav` — fixed left sidebar + main content area
- `top-nav` — horizontal navigation bar + full-width content
- `dashboard` — KPI cards + charts + recent activity table
- `form-page` — multi-section form with validation states
- `detail-page` — record detail with summary card + tabs + action bar
- `list-page` — searchable, filterable data table with pagination
- `wizard` — multi-step form with progress indicator
- `split-panel` — two-column: list on left, detail on right
- `login` — authentication screen (login, register, forgot password)
- `empty-state` — no data / first-use state with call-to-action
- `modal` — dialog overlay patterns (confirm, form, detail)

### Multi-Page Prototype Linking

When building multiple pages, link them with `<a href="page-name.html">`.
Generate an `index.html` that lists all prototype pages with descriptions.

```html
<!-- index.html — Prototype Navigation -->
<!DOCTYPE html>
<html>
<head>
  <title>[Project Name] — Prototype</title>
  <style>/* same design tokens */</style>
</head>
<body>
  <div class="prototype-index">
    <header>
      <h1>[Project Name] UI Prototype</h1>
      <p>Click any screen to view. Use browser back to return here.</p>
    </header>
    <div class="screen-grid">
      <a href="01-login.html" class="screen-card">
        <div class="screen-number">01</div>
        <h3>Login</h3>
        <p>User authentication screen</p>
        <div class="screen-meta">Role: All users</div>
      </a>
      <a href="02-dashboard.html" class="screen-card">
        <div class="screen-number">02</div>
        <h3>Dashboard</h3>
        <p>KPI overview and recent activity</p>
        <div class="screen-meta">Role: Manager</div>
      </a>
      <!-- repeat per page -->
    </div>
  </div>
</body>
</html>
```

---

## Phase 4 — OUTPUT

### File naming convention
```
[project-name]/
├── index.html                  ← prototype navigation hub
├── 01-[screen-name].html       ← first screen
├── 02-[screen-name].html       ← second screen
├── [shared-styles].html        ← if design tokens extracted to separate file
└── assets/                     ← any inline SVG icons or placeholder images
```

### Placeholder content rules

Use realistic placeholder data — not "Lorem ipsum" or "Placeholder text":
- Names: "Sarah Mitchell", "James Chen", "Ananya Patel"
- References: "ORD-2024-10847", "CUST-00234", "REF-GBP-5523"
- Amounts: "£14,280.00", "$3,491.50"
- Dates: use realistic dates in the near past/future
- Statuses: use real status values from the domain (PENDING, APPROVED, etc.)
- Numbers: use realistic quantities (not 1, 2, 3 — use 47, 183, 1,294)

### Interactive states to include (without JavaScript where possible)

- Hover states on all clickable elements (CSS `:hover`)
- Focus states on all form inputs (CSS `:focus-visible`)
- Active/selected state for nav items (CSS `.active` class)
- Disabled state example (HTML `disabled` attribute)
- Error state example on at least one form field
- Loading state placeholder (skeleton shimmer if relevant)

### Accessibility baseline

- `alt` text on all images
- `for`/`id` pairing on all labels and inputs
- Semantic HTML (`<nav>`, `<main>`, `<section>`, `<header>`, `<footer>`)
- Sufficient colour contrast (4.5:1 for body text, 3:1 for large text)
- Focus visible on keyboard-navigable elements

---

## Phase 5 — ITERATION LOOP

After delivering the first page, always offer:

```
Page delivered ✓

What's next?
  [A] Build another page in the same design system
  [B] Adjust this page (describe the change)
  [C] Extract the design system as a reusable CSS file
  [D] Add interactivity (show/hide panels, tab switching, modal open/close)
  [E] Make it mobile responsive
  [F] Export design tokens as JSON (for handoff to developers)
  [G] Done

Type a letter or describe what you'd like to change.
```

Keep the design token set consistent across ALL pages in a session.
If the user says "adjust the colours" or "change the font", update the
CSS variables block and regenerate — never hardcode values.

---

## Design Matching Rules (Clone Mode)

When matching an existing design, these rules are absolute:

1. **Colour must be exact** — use the extracted hex values, not approximations
2. **Spacing must feel the same** — if the original uses 24px card padding, use 24px
3. **Typography weight must match** — if headings are bold, make them bold
4. **Component shapes must match** — if buttons are pill-shaped, pills everywhere
5. **Shadow depth must match** — if the original is flat, stay flat; if elevated, stay elevated
6. **Border radius must match** — if cards have 12px radius, use 12px everywhere
7. **Navigation pattern must match** — if it's a sidebar app, keep the sidebar
8. **Density must match** — if it's compact/data-dense, keep it compact

The user must not be able to tell the difference between a page from the
original design and a new page built by this skill.
