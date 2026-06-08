# Homepage Astro Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the production homepage in the Astro site so it matches the approved mockup closely, loads automation metadata at build time, and supports client-side category and surface filtering with URL state.

**Architecture:** Keep the site prerendered with Astro and move automation discovery plus normalization into small typed utilities under `site/src/lib`. Render the homepage from focused Astro components, ship the renamed design-export assets from `site/public`, and use one small vanilla script to apply filters, update count text, and sync query params.

**Tech Stack:** Astro 6, TypeScript, static public assets, vanilla browser script, Node filesystem APIs, CSS in `site/src/styles/global.css`

---

### Task 1: Prepare site structure and homepage data plumbing

**Files:**
- Create: `site/src/layouts/BaseLayout.astro`
- Create: `site/src/components/home/HomeHero.astro`
- Create: `site/src/components/home/HomeFilters.astro`
- Create: `site/src/components/home/HomeCollectionMeta.astro`
- Create: `site/src/components/home/HomeGrid.astro`
- Create: `site/src/lib/automations.ts`
- Create: `site/src/lib/homepage.ts`
- Create: `site/src/data/site.ts`
- Modify: `site/src/pages/index.astro`
- Create: `site/src/styles/global.css`
- Test: `site/src/pages/index.astro`

- [ ] **Step 1: Write the failing integration expectation**

```ts
// Target behavior:
// - index.astro imports normalized automation data
// - page renders hero, filters, collection meta, and grid sections
// - cards include exact category and surface labels from metadata
```

- [ ] **Step 2: Run site build to confirm the current scaffold does not satisfy the homepage**

Run: `npm run build`
Expected: build succeeds, but rendered `dist/index.html` contains only the Astro starter markup and no homepage sections.

- [ ] **Step 3: Write the minimal data utilities and page structure**

```ts
// site/src/lib/automations.ts
export type AutomationEntry = {
  slug: string;
  title: string;
  description: string;
  categories: string[];
  surfaces: string[];
};
```

```astro
---astro
// site/src/pages/index.astro
import BaseLayout from '../layouts/BaseLayout.astro';
import HomeHero from '../components/home/HomeHero.astro';
import HomeFilters from '../components/home/HomeFilters.astro';
import HomeCollectionMeta from '../components/home/HomeCollectionMeta.astro';
import HomeGrid from '../components/home/HomeGrid.astro';
---
```

- [ ] **Step 4: Run the build again to verify the homepage structure renders**

Run: `npm run build`
Expected: build succeeds and `dist/index.html` includes the homepage section markup rather than the Astro starter page.

- [ ] **Step 5: Commit**

```bash
git add site/src/layouts/BaseLayout.astro site/src/components/home/HomeHero.astro site/src/components/home/HomeFilters.astro site/src/components/home/HomeCollectionMeta.astro site/src/components/home/HomeGrid.astro site/src/lib/automations.ts site/src/lib/homepage.ts site/src/data/site.ts site/src/pages/index.astro site/src/styles/global.css
git commit -m "feat(site): add homepage structure and data loading"
```

### Task 2: Ship renamed homepage assets and match the mockup styling

**Files:**
- Create: `site/public/media/home-hero.webm`
- Create: `site/public/logos/codex.png`
- Create: `site/public/logos/cursor.png`
- Create: `site/public/logos/claude.png`
- Modify: `site/src/components/home/HomeHero.astro`
- Modify: `site/src/styles/global.css`
- Test: `site/src/components/home/HomeHero.astro`

- [ ] **Step 1: Write the failing visual expectation**

```ts
// Target behavior:
// - hero uses the shipped WebM file
// - provider logos render from stable production filenames
// - CSS reproduces the monochrome editorial layout and boxed headline
```

- [ ] **Step 2: Confirm the production asset paths do not exist yet**

Run: `find public -maxdepth 3 -type f | sort`
Expected: no `public/media/home-hero.webm` or `public/logos/*.png` homepage asset files exist yet.

- [ ] **Step 3: Add renamed assets and homepage styling**

```css
/* site/src/styles/global.css */
:root {
  --page-max-width: 1240px;
  --border-strong: #000;
  --border-muted: #d8d8d8;
}
```

```astro
---astro
// site/src/components/home/HomeHero.astro
const heroVideoSrc = '/media/home-hero.webm';
const logos = [
  { src: '/logos/codex.png', alt: 'Codex' },
  { src: '/logos/cursor.png', alt: 'Cursor' },
  { src: '/logos/claude.png', alt: 'Claude' },
];
---
```

- [ ] **Step 4: Build and inspect the generated homepage asset references**

Run: `npm run build && rg "/media/home-hero.webm|/logos/codex.png|/logos/cursor.png|/logos/claude.png" dist/index.html`
Expected: build succeeds and the generated page references only the renamed production asset paths.

- [ ] **Step 5: Commit**

```bash
git add site/public/media/home-hero.webm site/public/logos/codex.png site/public/logos/cursor.png site/public/logos/claude.png site/src/components/home/HomeHero.astro site/src/styles/global.css
git commit -m "feat(site): add homepage visual assets and styling"
```

### Task 3: Add client-side filtering, URL state, and empty-state behavior

**Files:**
- Modify: `site/src/components/home/HomeFilters.astro`
- Modify: `site/src/components/home/HomeCollectionMeta.astro`
- Modify: `site/src/components/home/HomeGrid.astro`
- Modify: `site/src/pages/index.astro`
- Modify: `site/src/styles/global.css`
- Test: `site/dist/index.html`

- [ ] **Step 1: Write the failing behavior expectation**

```ts
// Target behavior:
// - filters toggle exact category and surface labels
// - count text updates from the filtered dataset
// - query params restore state on reload
// - no-match state appears when the intersection is empty
```

- [ ] **Step 2: Build the page and confirm there is no filtering script yet**

Run: `npm run build && rg "URLSearchParams|data-filter-group|data-automation-card" dist/index.html`
Expected: build succeeds, but the generated page contains no homepage filtering hooks yet.

- [ ] **Step 3: Add the smallest filtering script and required data attributes**

```html
<script is:inline>
  const params = new URLSearchParams(window.location.search);
  // Read category and surface values, update button state,
  // filter cards, update count text, and write URL params.
</script>
```

```astro
<!-- data attributes on cards -->
<article
  class="card"
  data-automation-card
  data-categories={entry.categories.join('||')}
  data-surfaces={entry.surfaces.join('||')}
>
```

- [ ] **Step 4: Rebuild and verify the filtering hooks are present**

Run: `npm run build && rg "data-filter-group|data-automation-card|URLSearchParams" dist/index.html`
Expected: build succeeds and the generated page includes the filtering hooks and inline script.

- [ ] **Step 5: Commit**

```bash
git add site/src/components/home/HomeFilters.astro site/src/components/home/HomeCollectionMeta.astro site/src/components/home/HomeGrid.astro site/src/pages/index.astro site/src/styles/global.css
git commit -m "feat(site): add homepage filters and URL state"
```

### Task 4: Verify the homepage against the spec gates

**Files:**
- Test: `site`

- [ ] **Step 1: Run Astro type and diagnostics checks**

Run: `npm run astro -- check`
Expected: exit code 0.

- [ ] **Step 2: Run the production build**

Run: `npm run build`
Expected: exit code 0 and a generated static homepage in `dist/`.

- [ ] **Step 3: Verify homepage content and filter coverage from built output**

Run: `rg "AI Agent Automations|data-filter-group|data-automation-card|No automations match" dist/index.html`
Expected: built output contains hero copy, filter controls, card hooks, and empty-state copy.

- [ ] **Step 4: Manual visual and behavior check**

Run: `npm run dev`
Expected: desktop and mobile browser review confirms mockup-aligned layout, full default list, category-only filtering, surface-only filtering, combined filtering, query-state restore, and empty-state rendering.

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "test(site): verify homepage implementation"
```
