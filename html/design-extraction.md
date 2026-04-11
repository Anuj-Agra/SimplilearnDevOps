# Design Extraction Guide

How to precisely extract a design system from an image or existing HTML file.

---

## Extracting from a Screenshot / Image

Work systematically through the image. Describe what you see in exact technical terms.

### Colour Extraction Method

1. Look at the **primary action button** — that hex is `--color-primary`
2. Look at the **page background** — that hex is `--color-bg`
3. Look at **card/panel backgrounds** — that hex is `--color-surface`
4. Look at **dividers/borders** — that hex is `--color-border`
5. Look at **body text** — that hex is `--color-text`
6. Look at **secondary/caption text** — that hex is `--color-text-secondary`
7. Look for **green** states (success badges) — `--color-success`
8. Look for **amber/orange** states (warnings, pending) — `--color-warning`
9. Look for **red** states (errors, destructive) — `--color-error`
10. Look at **button text** on coloured buttons — `--color-text-inverse`

**For dark themes**: the above still applies but surface > bg (darker bg, lighter surface).

### Typography Estimation

Without exact font names, describe precisely:
- Weight: Thin (100) / Light (300) / Regular (400) / Medium (500) / SemiBold (600) / Bold (700) / ExtraBold (800)
- Width: Condensed / Normal / Wide
- Style: Geometric / Humanist / Slab / Serif / Monospace
- Cap height: Low / Normal / Tall
- x-height: Low / Normal / High (affects perceived size)

Use Google Fonts to find the closest match. Common matches:
- Geometric sans: Inter, DM Sans, Outfit, Plus Jakarta Sans, Manrope
- Humanist sans: Source Sans, Nunito, Poppins
- Slab: Roboto Slab, Zilla Slab
- Financial/formal: IBM Plex Sans, Lato (medium-weight)
- Bold display: Sora, Lexend, Space Grotesk, Raleway

### Spacing Estimation

Measure visually relative to the most common element (usually a button or input):

**Base unit detection:**
- If gaps feel very tight → 4px base
- If gaps feel normal → 8px base (most common)
- If gaps feel generous → 12px or 16px base

Common spacing ratios to look for:
- Inner padding of small badges: 2-4px vertical, 6-10px horizontal
- Input/button padding: 8-12px vertical, 12-20px horizontal
- Card padding: 16-32px
- Section gaps: 24-48px

### Border Radius Estimation

- **Flat/Zero** (0px): sharp corners, usually enterprise/financial
- **Subtle** (2-4px): nearly sharp, slightly softened
- **Standard** (6-8px): modern SaaS standard
- **Rounded** (10-16px): friendly, consumer-facing
- **Very Rounded** (20px+): playful, marketing
- **Pill** (999px): always for badges, sometimes for buttons

Note: buttons and inputs often differ from cards. Observe each separately.

### Shadow Depth Detection

- **Flat** (no shadow): usually dark themes or highly minimal designs
- **Subtle** (box-shadow: 0 1px 3px rgba(0,0,0,0.08)): most modern SaaS
- **Medium** (0 4px 12px rgba(0,0,0,0.1)): cards that need to "lift"
- **Strong** (0 8px 24px rgba(0,0,0,0.15)): modals, dropdowns
- **Dramatic** (0 20px 40px rgba(0,0,0,0.2)): marketing/hero cards

---

## Extracting from an HTML File

### Step 1: Find all CSS custom properties (fastest method)

```bash
grep -oP "--[a-zA-Z0-9-]+:\s*[^;]+" <file>.html | sort | uniq
```

If custom properties exist, they ARE the design system. Extract all of them.

### Step 2: Find recurring colour values

```bash
grep -oP "#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)" <file>.html | sort | uniq -c | sort -rn | head -20
```

Most frequent colours = brand colours.

### Step 3: Find font references

```bash
grep -oP "font-family:\s*[^;]+" <file>.html | sort | uniq
grep -oP "fonts\.googleapis\.com/css[^\"']+" <file>.html
```

### Step 4: Find border radius values

```bash
grep -oP "border-radius:\s*[^;]+" <file>.html | sort | uniq -c | sort -rn
```

### Step 5: Find spacing patterns

```bash
grep -oP "padding:\s*[^;]+" <file>.html | sort | uniq -c | sort -rn | head -10
grep -oP "gap:\s*[^;]+" <file>.html | sort | uniq -c | sort -rn | head -10
```

---

## Design System Fingerprints

Recognise common design systems from visual patterns:

### Financial Services / Banking
- Navy or dark blue primary (`#0F2D54`, `#003087`, `#1B3A6B`)
- White or very light grey background
- Zero or minimal border radius
- Dense information layout, small font sizes
- Strong grid structure, heavy borders between sections
- Green for positive values, red for negative

### Modern SaaS (Neutral)
- Blue or purple primary
- Pure white background, grey surface
- 8px border radius standard
- 14px base font size, comfortable line height
- Shadow-sm on cards, no border sometimes
- Sidebar navigation

### Internal Tool / Admin
- Dark sidebar (near-black), white content area
- Compact spacing (4px base)
- Minimal styling — function over form
- Dense tables with many columns
- Small badges, status indicators everywhere

### Consumer / Public Facing
- Bright, saturated primary colour
- Generous whitespace (16px base)
- Large rounded corners (12-16px)
- Large typography (18-20px base)
- Minimal tables — cards and lists preferred

---

## Style Extraction Report Template

Fill this out before building any pages (Clone/Extend mode):

```
DESIGN SYSTEM EXTRACTED
═══════════════════════════════════════════════════

SOURCE: [image filename / html filename]
STYLE:  [e.g. "Financial services, formal, data-dense, navy/white"]

COLOURS:
  Primary:         [hex] — [where used]
  Primary hover:   [hex — darken by ~10%]
  Primary subtle:  [hex — lighten to ~8% opacity]
  Secondary:       [hex]
  Background:      [hex]
  Surface:         [hex]
  Border:          [hex]
  Text primary:    [hex]
  Text secondary:  [hex]
  Text inverse:    [hex]
  Success:         [hex]
  Warning:         [hex]
  Error:           [hex]

TYPOGRAPHY:
  Heading font:  [name] — weight [N] — tracking [tight/normal/wide]
  Body font:     [name] — weight [N] — size [N]px — line-height [N]
  Font source:   [Google Fonts URL or system]

SPACING:
  Base unit:     [N]px
  Card padding:  [N]px
  Gap between form fields: [N]px
  Section spacing: [N]px

COMPONENTS:
  Button shape:    [pill / rounded / square] — padding [Npx Npx]
  Input style:     [underline / bordered / filled]
  Card:            [border + shadow / shadow only / border only]
  Navigation:      [top / sidebar-light / sidebar-dark]
  Border radius:   buttons=[N] inputs=[N] cards=[N] badges=[N]
  Shadow:          [none / sm / md / lg]

DENSITY:  [Compact / Comfortable / Spacious]
THEME:    [Light / Dark]

═══════════════════════════════════════════════════
READY TO BUILD — applying this system to all new pages
```
