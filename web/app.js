/**
 * TOC Case Study (SET-E) — Log Analysis Web Dashboard Client
 * Course Code: 24CS52 — Theory of Computations (2026–2027)
 *
 * Interacts with the real Python backend API (/api/*) to invoke REAnalyzer
 * and DFAErrorScanner, updating the UI with exact returned values and spans.
 */

// Global Application State
const state = {
  rawMatches: [],        // Array of normalized match objects for Tab 1
  activeEngine: null,    // 'RE' | 'DFA' | null
  executionTimeMs: null, // Last execution time in ms
  patternsSummary: {},   // Object storing pattern counts if RE
  dfaMetadata: null,     // Formal DFA specification & transition matrix
};

// DOM Element Registry
const elements = {
  // Navigation & Drawers
  navTabs: document.querySelectorAll('.nav-tab'),
  tabPanels: document.querySelectorAll('.tab-panel'),
  btnToggleDrawer: document.getElementById('btn-toggle-drawer'),
  btnCloseDrawer: document.getElementById('btn-close-drawer'),
  theoryDrawer: document.getElementById('theory-drawer'),
  drawerBackdrop: document.getElementById('drawer-backdrop'),

  // Tab 1: Stream Analyzer
  logInput: document.getElementById('log-input'),
  btnLoadSample: document.getElementById('btn-load-sample'),
  btnClearLog: document.getElementById('btn-clear-log'),
  btnRunRe: document.getElementById('btn-run-re'),
  btnRunDfa: document.getElementById('btn-run-dfa'),
  loadingIndicator: document.getElementById('loading-indicator'),
  loadingText: document.getElementById('loading-text'),
  valLogSize: document.getElementById('val-log-size'),
  subLogLines: document.getElementById('sub-log-lines'),
  logStatsBadge: document.getElementById('log-stats-badge'),
  valTotalRe: document.getElementById('val-total-re'),
  subReTime: document.getElementById('sub-re-time'),
  valErrorCount: document.getElementById('val-error-count'),
  subErrorMatch: document.getElementById('sub-error-match'),
  valWarningCount: document.getElementById('val-warning-count'),
  resultsEngineBadge: document.getElementById('results-engine-badge'),
  patternPills: document.getElementById('pattern-pills'),
  filterPattern: document.getElementById('filter-pattern'),
  searchResults: document.getElementById('search-results'),
  resultsTbody: document.getElementById('results-tbody'),

  // Tab 2: Equivalence Comparator
  btnRunCompare: document.getElementById('btn-run-compare'),
  compareSummaryCard: document.getElementById('compare-summary-card'),
  parityStatusIcon: document.getElementById('parity-status-icon'),
  parityStatusTitle: document.getElementById('parity-status-title'),
  parityStatusDesc: document.getElementById('parity-status-desc'),
  compReCount: document.getElementById('comp-re-count'),
  compDfaCount: document.getElementById('comp-dfa-count'),
  compParityRate: document.getElementById('comp-parity-rate'),
  compareTbody: document.getElementById('compare-tbody'),

  // Tab 3: DFA Visualizer & Token Tracer
  btnRefreshDfaMeta: document.getElementById('btn-refresh-dfa-meta'),
  transitionMatrixTbody: document.getElementById('transition-matrix-tbody'),
  tracerInput: document.getElementById('tracer-input'),
  btnRunTrace: document.getElementById('btn-run-trace'),
  presetChips: document.querySelectorAll('.preset-chip'),
  tracerSummary: document.getElementById('tracer-summary'),
  tracerStepsTbody: document.getElementById('tracer-steps-tbody'),

  // Tab 4: Live Benchmark
  benchmarkIterations: document.getElementById('benchmark-iterations'),
  btnRunLiveBenchmark: document.getElementById('btn-run-live-benchmark'),
  benchmarkLoading: document.getElementById('benchmark-loading'),
  benchmarkLoadingText: document.getElementById('benchmark-loading-text'),
  benchmarkResultsView: document.getElementById('benchmark-results-view'),
  bReMedian: document.getElementById('b-re-median'),
  bReMean: document.getElementById('b-re-mean'),
  bReMin: document.getElementById('b-re-min'),
  bReMax: document.getElementById('b-re-max'),
  bReStdev: document.getElementById('b-re-stdev'),
  bDfaMedian: document.getElementById('b-dfa-median'),
  bDfaMean: document.getElementById('b-dfa-mean'),
  bDfaMin: document.getElementById('b-dfa-min'),
  bDfaMax: document.getElementById('b-dfa-max'),
  bDfaStdev: document.getElementById('b-dfa-stdev'),
  bAllMedian: document.getElementById('b-all-median'),
  bAllMean: document.getElementById('b-all-mean'),
  bAllMin: document.getElementById('b-all-min'),
  bAllMax: document.getElementById('b-all-max'),
  bAllStdev: document.getElementById('b-all-stdev'),
  benchAnalysisText: document.getElementById('bench-analysis-text'),
};

/**
 * Initialize application listeners, pre-load sample log, and fetch DFA metadata
 */
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupEventListeners();
  loadSampleLog();
  loadDfaMetadata();
  // Trace initial default token [ERROR]
  traceToken('[ERROR]');
});

/**
 * Tab and drawer navigation setup
 */
function setupNavigation() {
  // Tab switching
  elements.navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetPanelId = tab.dataset.tab;
      
      elements.navTabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      elements.tabPanels.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      const targetPanel = document.getElementById(targetPanelId);
      if (targetPanel) targetPanel.classList.add('active');
    });
  });

  // Drawer toggles
  if (elements.btnToggleDrawer) {
    elements.btnToggleDrawer.addEventListener('click', openTheoryDrawer);
  }
  if (elements.btnCloseDrawer) {
    elements.btnCloseDrawer.addEventListener('click', closeTheoryDrawer);
  }
  if (elements.drawerBackdrop) {
    elements.drawerBackdrop.addEventListener('click', closeTheoryDrawer);
  }
}

function openTheoryDrawer() {
  elements.theoryDrawer.classList.remove('hidden');
  elements.theoryDrawer.setAttribute('aria-hidden', 'false');
  elements.drawerBackdrop.classList.remove('hidden');
}

function closeTheoryDrawer() {
  elements.theoryDrawer.classList.add('hidden');
  elements.theoryDrawer.setAttribute('aria-hidden', 'true');
  elements.drawerBackdrop.classList.add('hidden');
}

/**
 * Setup main event listeners
 */
function setupEventListeners() {
  // Tab 1 Listeners
  elements.btnLoadSample.addEventListener('click', loadSampleLog);
  elements.btnClearLog.addEventListener('click', clearLog);
  elements.btnRunRe.addEventListener('click', runRegexAnalysis);
  elements.btnRunDfa.addEventListener('click', runDfaAnalysis);
  elements.logInput.addEventListener('input', updateInputMetrics);
  elements.filterPattern.addEventListener('change', renderTable);
  elements.searchResults.addEventListener('input', renderTable);

  // Tab 2 Listeners
  elements.btnRunCompare.addEventListener('click', runEquivalenceComparison);

  // Tab 3 Listeners
  elements.btnRefreshDfaMeta.addEventListener('click', loadDfaMetadata);
  elements.btnRunTrace.addEventListener('click', () => {
    const token = elements.tracerInput.value;
    traceToken(token);
  });
  elements.tracerInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      traceToken(elements.tracerInput.value);
    }
  });
  elements.presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const token = chip.dataset.token;
      elements.tracerInput.value = token;
      traceToken(token);
    });
  });

  // Tab 4 Listeners
  elements.btnRunLiveBenchmark.addEventListener('click', runLiveBenchmark);
}

/**
 * Updates textarea character and line counters
 */
function updateInputMetrics() {
  const text = elements.logInput.value;
  const chars = text.length;
  const lines = text ? text.split('\n').length : 0;
  
  elements.valLogSize.innerHTML = `${chars.toLocaleString()} <span class="metric-unit">chars</span>`;
  elements.subLogLines.textContent = `${lines.toLocaleString()} log entries`;
  elements.logStatsBadge.textContent = `${lines} lines | ${chars.toLocaleString()} chars`;
}

/**
 * Fetches the verified 30-entry sample log from /api/sample-log
 */
async function loadSampleLog() {
  showLoading('Loading verified sample log...');
  try {
    const res = await fetch('/api/sample-log');
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch sample log`);
    const data = await res.json();
    
    elements.logInput.value = data.text;
    updateInputMetrics();
  } catch (err) {
    showErrorState(`Failed to load sample log: ${err.message}`);
  } finally {
    hideLoading();
  }
}

function clearLog() {
  elements.logInput.value = '';
  updateInputMetrics();
  state.rawMatches = [];
  state.activeEngine = null;
  resetMetrics();
  renderTable();
}

function resetMetrics() {
  elements.valTotalRe.textContent = '-';
  elements.subReTime.textContent = 'Awaiting execution';
  elements.valErrorCount.textContent = '-';
  elements.subErrorMatch.textContent = 'RE / DFA target';
  elements.valWarningCount.textContent = '-';
  elements.resultsEngineBadge.className = 'engine-badge badge-neutral';
  elements.resultsEngineBadge.textContent = 'No active run';
  elements.patternPills.innerHTML = '';
}

/**
 * Executes the Python RE Analyzer via POST /api/analyze/re
 */
async function runRegexAnalysis() {
  const text = elements.logInput.value;
  if (!text.trim()) {
    alert('Please enter or load log text before analyzing.');
    return;
  }

  showLoading('Executing Python RE Analyzer across 5 patterns...');
  try {
    const res = await fetch('/api/analyze/re', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `Server responded with HTTP ${res.status}`);
    }

    const data = await res.json();
    state.activeEngine = 'RE';
    state.executionTimeMs = data.execution_time_ms;
    state.patternsSummary = data.patterns;

    // Flatten matches into single list
    const allMatches = [];
    for (const [patternName, patternData] of Object.entries(data.patterns)) {
      for (const m of patternData.matches) {
        allMatches.push(m);
      }
    }
    // Sort chronologically by start offset
    allMatches.sort((a, b) => a.start_offset - b.start_offset);
    state.rawMatches = allMatches;

    // Update UI Metrics
    elements.valTotalRe.textContent = data.total_matches;
    elements.subReTime.textContent = `Executed in ${data.execution_time_ms} ms`;
    
    const errCount = data.patterns['ERROR Keyword'] ? data.patterns['ERROR Keyword'].count : 0;
    const warnCount = data.patterns['WARNING Keyword'] ? data.patterns['WARNING Keyword'].count : 0;
    elements.valErrorCount.textContent = errCount;
    elements.valWarningCount.textContent = warnCount;
    elements.subErrorMatch.textContent = `Exact \\bERROR\\b matches`;

    elements.resultsEngineBadge.className = 'engine-badge badge-active-re';
    elements.resultsEngineBadge.textContent = `Regex Engine: ${data.total_matches} matches in ${data.execution_time_ms} ms`;

    renderPatternPills(data.patterns);
    renderTable();
  } catch (err) {
    showErrorState(`Regex Analysis Error: ${err.message}`);
  } finally {
    hideLoading();
  }
}

/**
 * Executes the pure Python DFA Scanner via POST /api/analyze/dfa
 */
async function runDfaAnalysis() {
  const text = elements.logInput.value;
  if (!text.trim()) {
    alert('Please enter or load log text before analyzing.');
    return;
  }

  showLoading('Executing manual 7-state DFA scanner for keyword ERROR...');
  try {
    const res = await fetch('/api/analyze/dfa', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `Server responded with HTTP ${res.status}`);
    }

    const data = await res.json();
    state.activeEngine = 'DFA';
    state.executionTimeMs = data.execution_time_ms;
    state.rawMatches = data.matches;

    // Update UI Metrics
    elements.valTotalRe.textContent = '-';
    elements.subReTime.textContent = 'DFA active (ERROR only)';
    elements.valErrorCount.textContent = data.total_matches;
    elements.subErrorMatch.textContent = `DFA 7-state scanner in ${data.execution_time_ms} ms`;
    elements.valWarningCount.textContent = '-';

    elements.resultsEngineBadge.className = 'engine-badge badge-active-dfa';
    elements.resultsEngineBadge.textContent = `DFA Scanner: ${data.total_matches} 'ERROR' matches in ${data.execution_time_ms} ms`;

    // Render single pill for DFA
    elements.patternPills.innerHTML = `
      <div class="pill-item">
        <span>ERROR Keyword (DFA)</span>
        <span class="pill-count pill-count-err">${data.total_matches}</span>
      </div>
    `;

    renderTable();
  } catch (err) {
    showErrorState(`DFA Scanner Error: ${err.message}`);
  } finally {
    hideLoading();
  }
}

/**
 * Renders pattern count pills under table header
 */
function renderPatternPills(patterns) {
  const pillClasses = {
    'Date (DD-MM-YYYY)': 'pill-count-date',
    'Time (HH:MM)': 'pill-count-time',
    'IPv4 Address': 'pill-count-ip',
    'ERROR Keyword': 'pill-count-err',
    'WARNING Keyword': 'pill-count-warn',
  };

  elements.patternPills.innerHTML = Object.entries(patterns).map(([name, p]) => {
    const badgeClass = pillClasses[name] || 'pill-count-ip';
    return `
      <div class="pill-item">
        <span>${escapeHtml(name)}</span>
        <span class="pill-count ${badgeClass}">${p.count}</span>
      </div>
    `;
  }).join('');
}

/**
 * Filters and renders match rows in Tab 1 results table
 */
function renderTable() {
  const filterType = elements.filterPattern.value;
  const searchQuery = elements.searchResults.value.toLowerCase().trim();

  const filtered = state.rawMatches.filter(m => {
    if (filterType !== 'ALL' && m.pattern_name !== filterType) {
      if (!(filterType === 'ERROR Keyword' && m.pattern_name.includes('ERROR'))) {
        return false;
      }
    }
    if (searchQuery) {
      const matchVal = m.value.toLowerCase();
      const lineText = m.line_text.toLowerCase();
      if (!matchVal.includes(searchQuery) && !lineText.includes(searchQuery)) {
        return false;
      }
    }
    return true;
  });

  if (filtered.length === 0) {
    const message = state.rawMatches.length === 0
      ? 'Click <strong>Run Regex Analyzer</strong> or <strong>Run DFA Scanner</strong> above to analyze the log stream.'
      : 'No matches found matching the selected filter criteria.';

    elements.resultsTbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="6">
          <div class="empty-state">
            <p class="empty-title">${state.rawMatches.length === 0 ? 'Ready for Analysis' : 'No Filter Matches'}</p>
            <p class="empty-desc">${message}</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  const tagClasses = {
    'Date (DD-MM-YYYY)': 'tag-date',
    'Time (HH:MM)': 'tag-time',
    'IPv4 Address': 'tag-ip',
    'ERROR Keyword': 'tag-error',
    'ERROR Keyword (DFA)': 'tag-error',
    'WARNING Keyword': 'tag-warning',
  };

  elements.resultsTbody.innerHTML = filtered.map((m, idx) => {
    const tagClass = tagClasses[m.pattern_name] || 'tag-ip';
    const spanText = `[${m.start_offset}:${m.end_offset})`;
    const lineCol = `L${m.line_number}:C${m.column_number}`;
    
    return `
      <tr>
        <td class="text-muted">${idx + 1}</td>
        <td><span class="text-muted" style="font-size: 11px;">${escapeHtml(m.pattern_name)}</span></td>
        <td><span class="val-tag ${tagClass}">${escapeHtml(m.value)}</span></td>
        <td><span class="span-code">${spanText}</span></td>
        <td><span class="coord-code">${lineCol}</span></td>
        <td><div class="context-snippet" title="${escapeHtml(m.line_text)}">${escapeHtml(m.line_text)}</div></td>
      </tr>
    `;
  }).join('');
}

/**
 * TAB 2: Equivalence Comparison between RE and DFA on ERROR
 */
async function runEquivalenceComparison() {
  const text = elements.logInput.value;
  if (!text.trim()) {
    alert('Please enter or load log text before running equivalence comparison.');
    return;
  }

  elements.btnRunCompare.disabled = true;
  elements.btnRunCompare.innerHTML = '<span class="spinner"></span> Comparing...';

  try {
    const res = await fetch('/api/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    renderEquivalenceResults(data);
  } catch (err) {
    alert(`Equivalence comparison failed: ${err.message}`);
  } finally {
    elements.btnRunCompare.disabled = false;
    elements.btnRunCompare.innerHTML = '<span class="btn-icon">⚡</span> Run Equivalence Verification';
  }
}

function renderEquivalenceResults(data) {
  elements.compReCount.textContent = data.re_count;
  elements.compDfaCount.textContent = data.dfa_count;

  if (data.overall_parity) {
    elements.compareSummaryCard.className = 'parity-summary-card parity-success';
    elements.parityStatusIcon.textContent = '✅';
    elements.parityStatusTitle.textContent = '100% Coordinate Parity Confirmed';
    elements.parityStatusDesc.textContent = `Both Python re (\\bERROR\\b) and the 7-state manual DFA found exactly ${data.re_count} matches with identical character offsets [start:end) and line:column coordinates.`;
    elements.compParityRate.innerHTML = '<span class="badge-match">100% MATCH</span>';
  } else {
    elements.compareSummaryCard.className = 'parity-summary-card parity-mismatch';
    elements.parityStatusIcon.textContent = '⚠️';
    elements.parityStatusTitle.textContent = 'Discrepancy Detected';
    elements.parityStatusDesc.textContent = `Regex found ${data.re_count} matches while DFA found ${data.dfa_count} matches. Inspect the highlighted rows below to diagnose coordinate drift.`;
    elements.compParityRate.innerHTML = '<span class="badge-drift">MISMATCH</span>';
  }

  if (data.comparison_items.length === 0) {
    elements.compareTbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="9">
          <div class="empty-state">
            <p class="empty-title">Zero ERROR Tokens Found</p>
            <p class="empty-desc">Neither engine detected any whole-word ERROR tokens in the provided input.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  elements.compareTbody.innerHTML = data.comparison_items.map(item => {
    const isEq = item.is_equal;
    const reSpan = item.re_span ? `[${item.re_span[0]}:${item.re_span[1]})` : '<span class="text-muted">None</span>';
    const dfaSpan = item.dfa_span ? `[${item.dfa_span[0]}:${item.dfa_span[1]})` : '<span class="text-muted">None</span>';
    const reCoord = (item.re_line !== null) ? `L${item.re_line}:C${item.re_col}` : '<span class="text-muted">-</span>';
    const dfaCoord = (item.dfa_line !== null) ? `L${item.dfa_line}:C${item.dfa_col}` : '<span class="text-muted">-</span>';
    const statusBadge = isEq 
      ? '<span class="badge-match">IDENTICAL</span>' 
      : '<span class="badge-drift">DRIFT</span>';

    return `
      <tr style="${isEq ? '' : 'background: rgba(239, 68, 68, 0.08);'}">
        <td class="text-muted">${item.index}</td>
        <td><span class="val-tag tag-error">${escapeHtml(item.re_value || '-')}</span></td>
        <td><span class="span-code">${reSpan}</span></td>
        <td><span class="coord-code">${reCoord}</span></td>
        <td><span class="val-tag tag-error">${escapeHtml(item.dfa_value || '-')}</span></td>
        <td><span class="span-code">${dfaSpan}</span></td>
        <td><span class="coord-code">${dfaCoord}</span></td>
        <td>${statusBadge}</td>
        <td><div class="context-snippet" title="${escapeHtml(item.line_text)}">${escapeHtml(item.line_text)}</div></td>
      </tr>
    `;
  }).join('');
}

/**
 * TAB 3: Load DFA Architecture & Transition Table from Python Backend
 */
async function loadDfaMetadata() {
  try {
    const res = await fetch('/api/dfa/metadata');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const meta = await res.json();
    state.dfaMetadata = meta;
    renderTransitionMatrix(meta.transition_table);
  } catch (err) {
    elements.transitionMatrixTbody.innerHTML = `
      <tr><td colspan="6" style="color: var(--color-error); text-align: center; padding: 20px;">
        Failed to load DFA specification: ${escapeHtml(err.message)}
      </td></tr>
    `;
  }
}

function renderTransitionMatrix(matrix) {
  const statesOrder = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q_word'];
  const alphabetOrder = ['E', 'R', 'O', 'OTHER_WORD', 'NON_WORD'];

  const rowsHtml = statesOrder.map(st => {
    const stateData = matrix[st] || {};
    const cellsHtml = alphabetOrder.map(cls => {
      const targetState = stateData[cls] || '-';
      let highlightClass = '';
      if (targetState === 'q0') highlightClass = 'state-highlight-q0';
      else if (targetState === 'q5') highlightClass = 'state-highlight-q5';
      else if (targetState === 'q_word') highlightClass = 'state-highlight-qword';
      else highlightClass = 'state-highlight-mid';

      return `<td class="${highlightClass}">${targetState}</td>`;
    }).join('');

    return `
      <tr>
        <td><strong>${st}</strong></td>
        ${cellsHtml}
      </tr>
    `;
  }).join('');

  elements.transitionMatrixTbody.innerHTML = rowsHtml;
}

/**
 * TAB 3: Step-by-Step DFA Token Tracer
 */
async function traceToken(token) {
  if (typeof token !== 'string') token = '';
  
  elements.btnRunTrace.disabled = true;
  elements.btnRunTrace.innerHTML = '<span class="spinner"></span> Tracing...';

  try {
    const res = await fetch('/api/dfa/trace', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    renderTraceResults(data);
  } catch (err) {
    alert(`Token trace failed: ${err.message}`);
  } finally {
    elements.btnRunTrace.disabled = false;
    elements.btnRunTrace.innerHTML = '<span class="btn-icon">▶</span> Trace Automaton';
  }
}

function renderTraceResults(data) {
  elements.tracerSummary.classList.remove('hidden', 'tracer-summary-success', 'tracer-summary-reject');

  if (data.total_matches > 0) {
    elements.tracerSummary.classList.add('tracer-summary-success');
    const spanStrs = data.matches.map(m => `[${m.start}:${m.end})`).join(', ');
    elements.tracerSummary.innerHTML = `
      <div><strong>Status: ACCEPTED (${data.total_matches} match found)</strong> — Spans: <code>${spanStrs}</code></div>
      <div>Final State: <code>${data.final_state}</code></div>
    `;
  } else {
    elements.tracerSummary.classList.add('tracer-summary-reject');
    elements.tracerSummary.innerHTML = `
      <div><strong>Status: REJECTED (0 whole-word ERROR matches emitted)</strong></div>
      <div>Final State: <code>${data.final_state}</code></div>
    `;
  }

  if (data.steps.length === 0) {
    elements.tracerStepsTbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="6">
          <div class="empty-state">
            <p class="empty-title">Empty Input Stream</p>
            <p class="empty-desc">The input string contains 0 characters. DFA remained at start state q0.</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  elements.tracerStepsTbody.innerHTML = data.steps.map(step => {
    const charDisplay = step.char === ' ' 
      ? '<span class="text-muted">&blank; [space]</span>' 
      : step.char === '\n' 
      ? '<span class="text-muted">\\n [newline]</span>' 
      : `<strong>${escapeHtml(step.char)}</strong>`;

    let notes = `<span class="text-muted">${escapeHtml(step.action)}</span>`;
    if (step.boundary_event) {
      notes += `<br><span style="color: ${step.boundary_event.includes('verified') ? '#34d399' : '#f87171'}; font-weight: 600;">${escapeHtml(step.boundary_event)}</span>`;
    }

    return `
      <tr>
        <td class="text-muted">${step.step}</td>
        <td><span class="val-tag" style="background: #1e293b;">${charDisplay}</span></td>
        <td><code>${escapeHtml(step.char_class)}</code></td>
        <td><span class="span-code">${escapeHtml(step.from_state)}</span></td>
        <td><span class="span-code" style="color: #60a5fa; font-weight: 700;">${escapeHtml(step.to_state)}</span></td>
        <td>${notes}</td>
      </tr>
    `;
  }).join('');

  if (data.eof_event) {
    elements.tracerStepsTbody.innerHTML += `
      <tr style="background: rgba(16, 185, 129, 0.1);">
        <td class="text-muted">EOF</td>
        <td colspan="2"><span class="badge badge-set">End-of-Input</span></td>
        <td><span class="span-code">q5</span></td>
        <td><span class="span-code" style="color: #34d399; font-weight: 700;">ACCEPT</span></td>
        <td style="color: #34d399; font-weight: 600;">${escapeHtml(data.eof_event)}</td>
      </tr>
    `;
  }
}

/**
 * TAB 4: Live Empirical Benchmark Runner
 */
async function runLiveBenchmark() {
  const text = elements.logInput.value;
  if (!text.trim()) {
    alert('Please enter or load log text before benchmarking.');
    return;
  }

  const iterations = parseInt(elements.benchmarkIterations.value, 10) || 50;

  elements.btnRunLiveBenchmark.disabled = true;
  elements.btnRunLiveBenchmark.innerHTML = '<span class="spinner"></span> Benchmarking...';
  elements.benchmarkLoading.classList.remove('hidden');
  elements.benchmarkLoadingText.textContent = `Running ${iterations} iterations in Python 3.13 backend...`;

  try {
    const res = await fetch('/api/benchmark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, iterations }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    renderBenchmarkResults(data);
  } catch (err) {
    alert(`Benchmark execution failed: ${err.message}`);
  } finally {
    elements.btnRunLiveBenchmark.disabled = false;
    elements.btnRunLiveBenchmark.innerHTML = '<span class="btn-icon">⚡</span> Run Fresh Benchmark';
    elements.benchmarkLoading.classList.add('hidden');
  }
}

function renderBenchmarkResults(data) {
  elements.benchmarkResultsView.classList.remove('hidden');

  const reA = data.workload_a_re_error_us;
  const dfaA = data.workload_a_dfa_error_us;
  const reB = data.workload_b_re_all_5_us;

  // Workload A (RE ERROR)
  elements.bReMedian.textContent = reA.median_us.toLocaleString();
  elements.bReMean.textContent = `${reA.mean_us.toLocaleString()} \u03bcs`;
  elements.bReMin.textContent = `${reA.min_us.toLocaleString()} \u03bcs`;
  elements.bReMax.textContent = `${reA.max_us.toLocaleString()} \u03bcs`;
  elements.bReStdev.textContent = `${reA.stdev_us.toLocaleString()} \u03bcs`;

  // Workload A (DFA ERROR)
  elements.bDfaMedian.textContent = dfaA.median_us.toLocaleString();
  elements.bDfaMean.textContent = `${dfaA.mean_us.toLocaleString()} \u03bcs`;
  elements.bDfaMin.textContent = `${dfaA.min_us.toLocaleString()} \u03bcs`;
  elements.bDfaMax.textContent = `${dfaA.max_us.toLocaleString()} \u03bcs`;
  elements.bDfaStdev.textContent = `${dfaA.stdev_us.toLocaleString()} \u03bcs`;

  // Workload B (RE All 5)
  elements.bAllMedian.textContent = reB.median_us.toLocaleString();
  elements.bAllMean.textContent = `${reB.mean_us.toLocaleString()} \u03bcs`;
  elements.bAllMin.textContent = `${reB.min_us.toLocaleString()} \u03bcs`;
  elements.bAllMax.textContent = `${reB.max_us.toLocaleString()} \u03bcs`;
  elements.bAllStdev.textContent = `${reB.stdev_us.toLocaleString()} \u03bcs`;

  // Dynamic analysis text
  const ratio = (dfaA.median_us / (reA.median_us || 1)).toFixed(1);
  elements.benchAnalysisText.innerHTML = `
    <strong>Empirical Benchmark Observations (${data.iterations} iterations, ${data.character_count.toLocaleString()} characters):</strong><br>
    &bull; <strong>Workload A (Like-for-like):</strong> CPython's <code>re</code> engine executed the <code>\\bERROR\\b</code> search at a median of <strong>${reA.median_us} &mu;s</strong>, while the manual Python DFA executed at <strong>${dfaA.median_us} &mu;s</strong> (a ratio of ~${ratio}x). This difference reflects implementation runtime: CPython's regular expressions run inside an optimized C-extension (<code>_sre</code>), whereas the manual DFA runs through Python interpreter bytecode with character-by-character loop dispatch.<br>
    &bull; <strong>Workload B (Separate Multi-Pattern Task):</strong> Extracting all 5 patterns simultaneously required a median of <strong>${reB.median_us} &mu;s</strong>. This demonstrates the operational trade-off: regular expressions provide concise declarative syntax for arbitrary sets of patterns, whereas manual DFAs require dedicated per-token state construction.
  `;
}

/**
 * Utility: Loading & Error helpers
 */
function showLoading(text) {
  elements.loadingText.textContent = text;
  elements.loadingIndicator.classList.remove('hidden');
}

function hideLoading() {
  elements.loadingIndicator.classList.add('hidden');
}

function showErrorState(msg) {
  elements.resultsTbody.innerHTML = `
    <tr class="empty-row">
      <td colspan="6">
        <div class="empty-state" style="color: var(--color-error);">
          <p class="empty-title">Execution Error</p>
          <p class="empty-desc" style="color: #fca5a5;">${escapeHtml(msg)}</p>
        </div>
      </td>
    </tr>
  `;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
