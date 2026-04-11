# Page Templates Reference

Full HTML scaffolds for every page type. Use as a starting structure,
then populate with the actual content, design tokens, and components.

---

## Template: Sidebar Navigation App

For: internal tools, SaaS dashboards, admin panels, financial platforms

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Page Title] — [App Name]</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=[ChosenFont]&display=swap" rel="stylesheet">
  <style>
    /* PASTE DESIGN TOKENS HERE */

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-body);
      font-size: var(--text-base);
      color: var(--color-text);
      background: var(--color-bg);
      display: flex;
      min-height: 100vh;
    }

    /* ── Sidebar ─────────────────────────────────────── */
    .sidebar {
      width: var(--sidebar-width);
      background: var(--color-surface);
      border-right: 1px solid var(--color-border);
      display: flex;
      flex-direction: column;
      position: fixed;
      top: 0; left: 0;
      height: 100vh;
      overflow-y: auto;
      z-index: 100;
    }

    .sidebar-logo {
      padding: var(--space-6);
      border-bottom: 1px solid var(--color-border);
      display: flex;
      align-items: center;
      gap: var(--space-3);
    }

    .sidebar-logo-mark {
      width: 32px; height: 32px;
      background: var(--color-primary);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--color-text-inverse);
      font-weight: var(--weight-bold);
      font-size: var(--text-sm);
    }

    .sidebar-logo-name {
      font-family: var(--font-heading);
      font-weight: var(--weight-bold);
      font-size: var(--text-base);
      color: var(--color-text);
    }

    .sidebar-nav {
      flex: 1;
      padding: var(--space-4) 0;
    }

    .nav-section-label {
      font-size: var(--text-xs);
      font-weight: var(--weight-semibold);
      color: var(--color-text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: var(--space-4) var(--space-4) var(--space-2);
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-2) var(--space-4);
      margin: 1px var(--space-2);
      border-radius: var(--radius-md);
      color: var(--color-text-secondary);
      text-decoration: none;
      font-size: var(--text-sm);
      font-weight: var(--weight-medium);
      transition: all 0.15s;
      cursor: pointer;
    }

    .nav-item:hover {
      background: var(--color-primary-subtle);
      color: var(--color-primary);
    }

    .nav-item.active {
      background: var(--color-primary-subtle);
      color: var(--color-primary);
      font-weight: var(--weight-semibold);
    }

    .nav-item-icon {
      width: 18px; height: 18px;
      flex-shrink: 0;
      opacity: 0.7;
    }

    .nav-item.active .nav-item-icon { opacity: 1; }

    .nav-badge {
      margin-left: auto;
      background: var(--color-primary);
      color: var(--color-text-inverse);
      font-size: var(--text-xs);
      font-weight: var(--weight-bold);
      padding: 2px 6px;
      border-radius: var(--radius-full);
    }

    .sidebar-footer {
      padding: var(--space-4);
      border-top: 1px solid var(--color-border);
    }

    .user-card {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-3);
      border-radius: var(--radius-md);
      cursor: pointer;
    }

    .user-card:hover { background: var(--color-primary-subtle); }

    .user-avatar {
      width: 32px; height: 32px;
      border-radius: var(--radius-full);
      background: var(--color-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--color-text-inverse);
      font-size: var(--text-xs);
      font-weight: var(--weight-bold);
      flex-shrink: 0;
    }

    .user-info { flex: 1; min-width: 0; }
    .user-name { font-size: var(--text-sm); font-weight: var(--weight-semibold); color: var(--color-text); }
    .user-role { font-size: var(--text-xs); color: var(--color-text-secondary); }

    /* ── Main Content ─────────────────────────────────── */
    .main-content {
      margin-left: var(--sidebar-width);
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    .page-header {
      background: var(--color-surface);
      border-bottom: 1px solid var(--color-border);
      padding: 0 var(--space-8);
      height: var(--nav-height);
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .page-header-left {
      display: flex;
      align-items: center;
      gap: var(--space-4);
    }

    .breadcrumb {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
    }

    .breadcrumb-sep { opacity: 0.4; }
    .breadcrumb-current { color: var(--color-text); font-weight: var(--weight-medium); }

    .page-header-actions {
      display: flex;
      align-items: center;
      gap: var(--space-3);
    }

    .page-body {
      padding: var(--space-8);
      flex: 1;
      max-width: var(--max-width);
      width: 100%;
    }

    .page-title-row {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: var(--space-8);
    }

    .page-title {
      font-family: var(--font-heading);
      font-size: var(--text-3xl);
      font-weight: var(--weight-bold);
      color: var(--color-text);
      line-height: var(--leading-tight);
    }

    .page-subtitle {
      font-size: var(--text-base);
      color: var(--color-text-secondary);
      margin-top: var(--space-1);
    }
  </style>
</head>
<body>

  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="sidebar-logo">
      <div class="sidebar-logo-mark">A</div>
      <span class="sidebar-logo-name">[App Name]</span>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-section-label">Main</div>
      <a href="01-dashboard.html" class="nav-item active">
        <svg class="nav-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        Dashboard
      </a>
      <a href="02-list.html" class="nav-item">
        <svg class="nav-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        [Module Name]
        <span class="nav-badge">12</span>
      </a>
      <!-- More nav items -->
    </nav>

    <div class="sidebar-footer">
      <div class="user-card">
        <div class="user-avatar">SM</div>
        <div class="user-info">
          <div class="user-name">Sarah Mitchell</div>
          <div class="user-role">Senior Manager</div>
        </div>
      </div>
    </div>
  </aside>

  <!-- MAIN CONTENT -->
  <div class="main-content">
    <header class="page-header">
      <div class="page-header-left">
        <div class="breadcrumb">
          <span>[Module]</span>
          <span class="breadcrumb-sep">›</span>
          <span class="breadcrumb-current">[Current Page]</span>
        </div>
      </div>
      <div class="page-header-actions">
        <!-- Header action buttons -->
      </div>
    </header>

    <main class="page-body">
      <div class="page-title-row">
        <div>
          <h1 class="page-title">[Page Title]</h1>
          <p class="page-subtitle">[Page description]</p>
        </div>
        <div style="display:flex;gap:var(--space-3);">
          <!-- Primary action buttons -->
        </div>
      </div>

      <!-- PAGE CONTENT HERE -->

    </main>
  </div>

</body>
</html>
```

---

## Template: Top Navigation App

For: marketing sites, consumer apps, public-facing portals

```html
<!-- Replace sidebar structure with: -->
<header class="top-nav">
  <div class="nav-inner">
    <div class="nav-logo">
      <div class="logo-mark"></div>
      <span class="logo-name">[App Name]</span>
    </div>
    <nav class="nav-links">
      <a href="#" class="nav-link active">[Section 1]</a>
      <a href="#" class="nav-link">[Section 2]</a>
      <a href="#" class="nav-link">[Section 3]</a>
    </nav>
    <div class="nav-actions">
      <button class="btn btn-ghost">Sign in</button>
      <button class="btn btn-primary">Get started</button>
    </div>
  </div>
</header>

<main class="page-main">
  <!-- content -->
</main>

<style>
  .top-nav {
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    position: sticky; top: 0; z-index: 100;
    height: var(--nav-height);
  }
  .nav-inner {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 var(--space-8);
    height: 100%;
    display: flex;
    align-items: center;
    gap: var(--space-8);
  }
  .nav-links { display: flex; gap: var(--space-1); flex: 1; }
  .nav-link {
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    color: var(--color-text-secondary);
    text-decoration: none;
    transition: all 0.15s;
  }
  .nav-link:hover, .nav-link.active {
    color: var(--color-primary);
    background: var(--color-primary-subtle);
  }
  .page-main {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: var(--space-12) var(--space-8);
  }
</style>
```

---

## Template: Form Page

```html
<div class="form-page">
  <div class="form-page-header">
    <h1 class="page-title">Create [Entity]</h1>
    <p class="page-subtitle">Complete all required fields to [action].</p>
  </div>

  <form class="form-layout" novalidate>
    <!-- Section -->
    <section class="form-section">
      <div class="form-section-header">
        <h2 class="form-section-title">Section Title</h2>
        <p class="form-section-desc">Optional description of this section.</p>
      </div>
      <div class="form-grid">
        <div class="field">
          <label class="field-label" for="f1">Full Name <span class="required">*</span></label>
          <input class="field-input" id="f1" type="text" placeholder="e.g. Sarah Mitchell">
        </div>
        <div class="field">
          <label class="field-label" for="f2">Email Address <span class="required">*</span></label>
          <input class="field-input field-error" id="f2" type="email" placeholder="name@company.com" value="invalid-email">
          <span class="field-error-msg">Please enter a valid email address.</span>
        </div>
        <div class="field field-full">
          <label class="field-label" for="f3">Notes</label>
          <textarea class="field-input" id="f3" rows="4" placeholder="Any additional context..."></textarea>
          <span class="field-hint">Optional — visible to all team members.</span>
        </div>
      </div>
    </section>

    <div class="form-actions">
      <a href="javascript:history.back()" class="btn btn-ghost">Cancel</a>
      <button type="submit" class="btn btn-primary">Save [Entity]</button>
    </div>
  </form>
</div>

<style>
  .form-layout {
    max-width: 800px;
  }
  .form-section {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-8);
    margin-bottom: var(--space-6);
  }
  .form-section-header { margin-bottom: var(--space-6); }
  .form-section-title {
    font-size: var(--text-lg);
    font-weight: var(--weight-semibold);
    color: var(--color-text);
  }
  .form-section-desc {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    margin-top: var(--space-1);
  }
  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-5);
  }
  .field-full { grid-column: 1 / -1; }

  .field { display: flex; flex-direction: column; gap: var(--space-1); }
  .field-label {
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    color: var(--color-text);
  }
  .required { color: var(--color-error); margin-left: 2px; }
  .field-input {
    padding: var(--space-3) var(--space-4);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
    font-family: var(--font-body);
    color: var(--color-text);
    background: var(--color-bg);
    transition: border-color 0.15s, box-shadow 0.15s;
    resize: vertical;
  }
  .field-input:focus {
    outline: none;
    border-color: var(--color-border-focus);
    box-shadow: 0 0 0 3px var(--color-primary-subtle);
  }
  .field-input.field-error { border-color: var(--color-error); }
  .field-input.field-error:focus { box-shadow: 0 0 0 3px var(--color-error-subtle); }
  .field-error-msg { font-size: var(--text-xs); color: var(--color-error); }
  .field-hint { font-size: var(--text-xs); color: var(--color-text-secondary); }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3);
    padding-top: var(--space-4);
  }
</style>
```

---

## Template: Detail / Record Page

```html
<!-- Summary card at top + tabs for sections -->
<div class="detail-page">

  <!-- Status bar -->
  <div class="detail-status-bar">
    <div class="detail-status-left">
      <a href="javascript:history.back()" class="back-link">← Back to [List]</a>
    </div>
    <div class="detail-status-right">
      <span class="badge badge-warning">Pending Approval</span>
      <button class="btn btn-ghost">Edit</button>
      <button class="btn btn-primary">Approve</button>
      <button class="btn btn-danger">Reject</button>
    </div>
  </div>

  <!-- Summary header card -->
  <div class="detail-header-card">
    <div class="detail-header-main">
      <h1 class="detail-title">ORD-2024-10847</h1>
      <p class="detail-meta">Created 14 Jan 2025 by Sarah Mitchell · Last updated 2 hours ago</p>
    </div>
    <div class="detail-kpis">
      <div class="kpi">
        <span class="kpi-label">Total Value</span>
        <span class="kpi-value">£14,280.00</span>
      </div>
      <div class="kpi">
        <span class="kpi-label">Items</span>
        <span class="kpi-value">8</span>
      </div>
      <div class="kpi">
        <span class="kpi-label">Customer</span>
        <span class="kpi-value">Acme Corp Ltd</span>
      </div>
    </div>
  </div>

  <!-- Tab navigation -->
  <div class="tab-bar">
    <button class="tab active">Details</button>
    <button class="tab">Line Items</button>
    <button class="tab">History</button>
    <button class="tab">Documents</button>
  </div>

  <!-- Tab content -->
  <div class="tab-content">
    <!-- Active tab content here -->
  </div>

</div>

<style>
  .detail-status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-6);
  }
  .back-link {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    text-decoration: none;
  }
  .back-link:hover { color: var(--color-primary); }
  .detail-status-right { display: flex; align-items: center; gap: var(--space-3); }

  .detail-header-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-8);
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: var(--space-6);
    box-shadow: var(--shadow-sm);
  }
  .detail-title {
    font-family: var(--font-heading);
    font-size: var(--text-2xl);
    font-weight: var(--weight-bold);
    color: var(--color-text);
  }
  .detail-meta {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    margin-top: var(--space-2);
  }
  .detail-kpis { display: flex; gap: var(--space-8); }
  .kpi { display: flex; flex-direction: column; gap: var(--space-1); text-align: right; }
  .kpi-label { font-size: var(--text-xs); color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.06em; }
  .kpi-value { font-size: var(--text-xl); font-weight: var(--weight-bold); color: var(--color-text); }

  .tab-bar {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--color-border);
    margin-bottom: var(--space-6);
  }
  .tab {
    padding: var(--space-3) var(--space-6);
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    color: var(--color-text-secondary);
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: all 0.15s;
    margin-bottom: -1px;
  }
  .tab:hover { color: var(--color-text); }
  .tab.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
    font-weight: var(--weight-semibold);
  }
</style>
```

---

## Template: Dashboard (KPI + Charts + Table)

```html
<!-- KPI row -->
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-card-header">
      <span class="kpi-card-label">Total Orders</span>
      <span class="kpi-trend positive">↑ 12%</span>
    </div>
    <div class="kpi-card-value">1,847</div>
    <div class="kpi-card-sub">vs 1,649 last month</div>
  </div>
  <!-- repeat 3-4 KPI cards -->
</div>

<!-- Charts row -->
<div class="chart-grid">
  <div class="chart-card chart-large">
    <div class="chart-header">
      <h3 class="chart-title">Orders Over Time</h3>
      <div class="chart-controls"><!-- period selector --></div>
    </div>
    <div class="chart-body">
      <canvas id="lineChart" height="250"></canvas>
    </div>
  </div>
  <div class="chart-card">
    <div class="chart-header"><h3 class="chart-title">By Status</h3></div>
    <div class="chart-body">
      <canvas id="doughnutChart" height="200"></canvas>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  // Line chart
  new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
      labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul'],
      datasets: [{
        label: 'Orders',
        data: [1200, 1450, 1380, 1620, 1540, 1780, 1847],
        borderColor: 'var(--color-primary)',
        backgroundColor: 'rgba(var(--color-primary-rgb), 0.08)',
        fill: true, tension: 0.4, pointRadius: 4
      }]
    },
    options: { responsive: true, plugins: { legend: { display: false } } }
  });
</script>

<style>
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-5);
    margin-bottom: var(--space-8);
  }
  .kpi-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
  }
  .kpi-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3);
  }
  .kpi-card-label {
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    color: var(--color-text-secondary);
  }
  .kpi-trend {
    font-size: var(--text-xs);
    font-weight: var(--weight-semibold);
    padding: 2px 6px;
    border-radius: var(--radius-full);
  }
  .kpi-trend.positive {
    color: var(--color-success);
    background: var(--color-success-subtle);
  }
  .kpi-trend.negative {
    color: var(--color-error);
    background: var(--color-error-subtle);
  }
  .kpi-card-value {
    font-family: var(--font-heading);
    font-size: var(--text-3xl);
    font-weight: var(--weight-bold);
    color: var(--color-text);
    line-height: 1;
  }
  .kpi-card-sub {
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
    margin-top: var(--space-2);
  }
  .chart-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--space-5);
    margin-bottom: var(--space-8);
  }
  .chart-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    box-shadow: var(--shadow-sm);
  }
  .chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-5);
  }
  .chart-title {
    font-size: var(--text-base);
    font-weight: var(--weight-semibold);
    color: var(--color-text);
  }
</style>
```

---

## Shared Component CSS (buttons, badges, table, alerts)

```css
/* ── Buttons ─────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s;
  text-decoration: none;
  white-space: nowrap;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}
.btn-primary:hover:not(:disabled) { background: var(--color-primary-hover); }

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border-color: var(--color-border);
  box-shadow: var(--shadow-sm);
}
.btn-secondary:hover:not(:disabled) { background: var(--color-primary-subtle); border-color: var(--color-primary); }

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}
.btn-ghost:hover:not(:disabled) { background: var(--color-primary-subtle); color: var(--color-primary); }

.btn-danger {
  background: transparent;
  color: var(--color-error);
  border-color: var(--color-error);
}
.btn-danger:hover:not(:disabled) { background: var(--color-error-subtle); }

/* ── Badges ─────────────────────────────────────────── */
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
}
.badge-success  { background: var(--color-success-subtle);  color: var(--color-success); }
.badge-warning  { background: var(--color-warning-subtle);  color: var(--color-warning); }
.badge-error    { background: var(--color-error-subtle);    color: var(--color-error); }
.badge-primary  { background: var(--color-primary-subtle);  color: var(--color-primary); }
.badge-neutral  { background: var(--color-border);          color: var(--color-text-secondary); }

/* ── Data Table ─────────────────────────────────────── */
.table-wrapper {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  padding: var(--space-3) var(--space-5);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}
.data-table td {
  padding: var(--space-4) var(--space-5);
  font-size: var(--text-sm);
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
}
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover td { background: var(--color-primary-subtle); }
.data-table .col-actions { text-align: right; }

/* ── Alert ──────────────────────────────────────────── */
.alert {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid;
}
.alert-success { background: var(--color-success-subtle); border-color: var(--color-success); }
.alert-warning { background: var(--color-warning-subtle); border-color: var(--color-warning); }
.alert-error   { background: var(--color-error-subtle);   border-color: var(--color-error); }
.alert-icon { font-size: var(--text-lg); flex-shrink: 0; margin-top: 2px; }
.alert-title { font-weight: var(--weight-semibold); font-size: var(--text-sm); }
.alert-body  { font-size: var(--text-sm); color: var(--color-text-secondary); margin-top: var(--space-1); }
```
