# SkillForge

**AI-Powered Skill, Agent & Script Prompt Generator — for GitHub Copilot Chat**

SkillForge is a lightweight, browser-based tool that helps you design and generate production-ready AI skills, agent system prompts, and Python automation scripts. It works by generating optimized prompts that you paste into GitHub Copilot Chat (or any LLM), then lets you organize, preview, and export the results.

## Project Structure

```
skillforge/
├── index.html       # HTML shell — entry point, open in browser
├── styles.css       # All styling (CSS variables, layout, components)
├── prompts.js       # Prompt templates for analysis & generation (edit these!)
├── app.js           # Application logic (state, navigation, rendering, export)
└── README.md        # This file
```

## Quick Start

1. Open `index.html` in any modern browser
2. Describe your problem statement
3. Copy the generated analysis prompt → paste into Copilot Chat
4. Paste back Copilot's JSON response → parse the blueprint
5. For each component, copy the generation prompt → paste into Copilot → paste back the output
6. Export everything as a ZIP

## Customization

### Editing Prompt Templates

All prompt templates live in `prompts.js`. You can customize:

- `ANALYSIS_PROMPT_TEMPLATE` — controls how the problem is analyzed and decomposed into components
- `TYPE_INSTRUCTIONS` — per-type generation instructions (skill, agent, script)
- `buildGenerationPrompt()` — assembles the full generation prompt with project context

### Adding New Component Types

1. Add the type to `TYPE_INSTRUCTIONS` in `prompts.js`
2. Add badge color in `styles.css` (`.badge-yourtype`)
3. Add file extension mapping in `app.js` (`FILE_EXTS`)
4. Add badge label in `app.js` (`BADGE_LABELS`)

### Theming

All colors are CSS custom properties in `styles.css` under `:root`. Change them to match your brand.

## Dependencies

- **Zero build tools** — no npm, no bundler, no framework
- **JSZip** (loaded from CDN) — only used for ZIP export
- **Google Fonts** (loaded from CDN) — DM Sans, JetBrains Mono, Syne

## Browser Support

Any modern browser (Chrome, Firefox, Safari, Edge). No IE support.

## License

MIT — use it however you want.
