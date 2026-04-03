from __future__ import annotations

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Enterprise Architecture Agent</title>
    <style>
      :root {
        --bg: #eef2ff;
        --panel: rgba(255, 255, 255, 0.9);
        --panel-strong: #ffffff;
        --line: #d7def3;
        --text: #172033;
        --muted: #63708d;
        --brand: #335cff;
        --brand-dark: #1f45dc;
        --brand-soft: #e4ebff;
        --accent: #0f9d8a;
        --shadow: 0 22px 50px rgba(31, 47, 97, 0.12);
        --radius-xl: 28px;
        --radius-lg: 20px;
        --radius-md: 14px;
        --mono: "SFMono-Regular", "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
        --sans: "Segoe UI", "Aptos", "Helvetica Neue", Arial, sans-serif;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: var(--sans);
        color: var(--text);
        background:
          radial-gradient(circle at top left, rgba(84, 114, 255, 0.22), transparent 32%),
          radial-gradient(circle at bottom right, rgba(15, 157, 138, 0.16), transparent 28%),
          linear-gradient(180deg, #f7f9ff 0%, #eef3ff 100%);
      }

      .shell {
        min-height: 100vh;
        padding: 24px;
      }

      .frame {
        max-width: 1560px;
        margin: 0 auto;
        border: 1px solid rgba(215, 222, 243, 0.9);
        border-radius: 32px;
        background: rgba(255, 255, 255, 0.68);
        box-shadow: var(--shadow);
        backdrop-filter: blur(18px);
        overflow: hidden;
      }

      .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 18px 24px;
        background: rgba(255, 255, 255, 0.78);
        border-bottom: 1px solid rgba(215, 222, 243, 0.9);
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 14px;
      }

      .brand-badge {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, #335cff, #5f83ff);
        color: white;
        font-weight: 700;
        letter-spacing: 0.08em;
      }

      .brand-copy h1 {
        margin: 0;
        font-size: 18px;
        font-weight: 700;
      }

      .brand-copy p {
        margin: 3px 0 0;
        color: var(--muted);
        font-size: 13px;
      }

      .status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        border-radius: 999px;
        background: var(--brand-soft);
        color: #2740b0;
        font-size: 13px;
        font-weight: 600;
      }

      .status::before {
        content: "";
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: var(--accent);
        box-shadow: 0 0 0 6px rgba(15, 157, 138, 0.12);
      }

      .workspace {
        display: grid;
        grid-template-columns: 360px minmax(0, 1fr);
        min-height: calc(100vh - 120px);
      }

      .sidebar {
        padding: 24px;
        border-right: 1px solid rgba(215, 222, 243, 0.9);
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.7), rgba(243, 247, 255, 0.96));
      }

      .panel {
        background: var(--panel);
        border: 1px solid rgba(215, 222, 243, 0.9);
        border-radius: var(--radius-xl);
        padding: 22px;
        box-shadow: 0 18px 30px rgba(67, 87, 153, 0.08);
      }

      .panel h2 {
        margin: 0 0 10px;
        font-size: 22px;
      }

      .panel-copy {
        margin: 0 0 22px;
        color: var(--muted);
        line-height: 1.5;
        font-size: 14px;
      }

      .field {
        display: grid;
        gap: 8px;
        margin-bottom: 18px;
      }

      .field label {
        font-size: 13px;
        font-weight: 700;
        color: #30405d;
      }

      textarea {
        width: 100%;
        min-height: 260px;
        resize: vertical;
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px 18px;
        font: inherit;
        color: var(--text);
        background: rgba(248, 250, 255, 0.9);
        outline: none;
        transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
      }

      textarea:focus {
        border-color: #6d8aff;
        box-shadow: 0 0 0 4px rgba(51, 92, 255, 0.12);
        transform: translateY(-1px);
      }

      select {
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 14px 16px;
        font: inherit;
        color: var(--text);
        background: rgba(248, 250, 255, 0.9);
        outline: none;
        transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
      }

      select:focus {
        border-color: #6d8aff;
        box-shadow: 0 0 0 4px rgba(51, 92, 255, 0.12);
        transform: translateY(-1px);
      }

      .hint {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.5;
      }

      .actions {
        display: flex;
        gap: 12px;
        margin-top: 18px;
      }

      button {
        border: 0;
        border-radius: 14px;
        padding: 13px 18px;
        font: inherit;
        font-weight: 700;
        cursor: pointer;
        transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease;
      }

      button:hover {
        transform: translateY(-1px);
      }

      button:disabled {
        cursor: wait;
        opacity: 0.7;
        transform: none;
      }

      .primary {
        color: white;
        background: linear-gradient(135deg, var(--brand), var(--brand-dark));
        box-shadow: 0 16px 32px rgba(51, 92, 255, 0.28);
      }

      .secondary {
        color: #2740b0;
        background: var(--brand-soft);
      }

      .content {
        padding: 24px;
        overflow: auto;
      }

      .hero,
      .result-shell {
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(215, 222, 243, 0.92);
        border-radius: 30px;
        box-shadow: 0 20px 38px rgba(67, 87, 153, 0.08);
      }

      .hero {
        min-height: 100%;
        display: grid;
        place-items: center;
        padding: 40px;
      }

      .hero-card {
        max-width: 760px;
        text-align: center;
      }

      .hero-icon {
        width: 96px;
        height: 96px;
        margin: 0 auto 22px;
        border-radius: 999px;
        background:
          radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.85), transparent 35%),
          linear-gradient(145deg, rgba(51, 92, 255, 0.18), rgba(15, 157, 138, 0.15));
        border: 1px solid rgba(153, 168, 221, 0.5);
        display: grid;
        place-items: center;
      }

      .hero-icon::before {
        content: "";
        width: 48px;
        height: 34px;
        border-radius: 10px;
        background:
          linear-gradient(180deg, rgba(51, 92, 255, 0.22), rgba(51, 92, 255, 0.08)),
          white;
        box-shadow:
          0 0 0 1px rgba(51, 92, 255, 0.12),
          0 12px 24px rgba(51, 92, 255, 0.14);
      }

      .hero h3 {
        margin: 0 0 12px;
        font-size: 30px;
        line-height: 1.18;
      }

      .hero p {
        margin: 0;
        font-size: 16px;
        color: var(--muted);
        line-height: 1.75;
      }

      .result-shell {
        display: none;
        padding: 22px;
        gap: 22px;
      }

      .result-shell.visible {
        display: grid;
      }

      .result-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 18px;
        flex-wrap: wrap;
      }

      .eyebrow {
        margin: 0 0 6px;
        color: #3350c7;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.12em;
        font-weight: 800;
      }

      .result-head h3 {
        margin: 0;
        font-size: 28px;
      }

      .result-head p {
        margin: 10px 0 0;
        color: var(--muted);
      }

      .download-actions {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
      }

      .section-grid {
        display: grid;
        gap: 16px;
      }

      .section-card,
      .diagram-card {
        border: 1px solid rgba(215, 222, 243, 0.92);
        border-radius: 22px;
        background: var(--panel-strong);
        box-shadow: 0 14px 28px rgba(67, 87, 153, 0.06);
      }

      .section-card h4,
      .diagram-card h4 {
        margin: 0 0 12px;
        font-size: 17px;
      }

      .section-grid {
        grid-template-columns: 1fr;
      }

      .section-card {
        padding: 20px 22px 22px;
      }

      .section-title {
        font-size: 18px;
        font-weight: 800;
        color: #172554;
        margin-bottom: 14px;
      }

      .section-lines {
        display: grid;
        gap: 10px;
        padding-left: 10px;
        border-left: 3px solid #d9e3ff;
      }

      .detail-line {
        color: #334155;
        line-height: 1.75;
        font-size: 15px;
        padding-left: 16px;
        text-indent: -16px;
      }

      .detail-line strong {
        color: #0f172a;
        font-weight: 800;
      }

      .detail-subheading {
        margin-top: 4px;
        padding: 10px 12px;
        border-radius: 12px;
        background: linear-gradient(135deg, #edf3ff, #f8fbff);
        border: 1px solid #d6e2ff;
        color: #17336b;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0.01em;
      }

      .detail-line code {
        padding: 2px 6px;
        border-radius: 8px;
        background: #eff4ff;
        color: #1d4ed8;
        font-family: var(--mono);
        font-size: 0.92em;
      }

      .detail-line.bullet::before {
        content: "• ";
        color: #335cff;
        font-weight: 900;
      }

      .diagram-layout {
        display: grid;
        grid-template-columns: 1fr;
        gap: 16px;
      }

      .diagram-card {
        padding: 18px;
      }

      .diagram-stage {
        border-radius: 20px;
        border: 1px solid rgba(215, 222, 243, 0.92);
        background:
          linear-gradient(180deg, rgba(247, 250, 255, 0.96), rgba(241, 246, 255, 0.96));
        min-height: 660px;
        overflow: auto;
        position: relative;
      }

      .diagram-stage svg {
        display: block;
        width: 100%;
        min-width: 960px;
        height: auto;
      }

      .inline-note {
        margin-top: 10px;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.55;
      }

      .message {
        display: none;
        margin-top: 14px;
        padding: 12px 14px;
        border-radius: 14px;
        font-size: 13px;
        line-height: 1.5;
      }

      .message.visible {
        display: block;
      }

      .message.error {
        background: #fff1f2;
        color: #be123c;
        border: 1px solid #fecdd3;
      }

      .message.success {
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
      }

      @media (max-width: 1200px) {
        .workspace {
          grid-template-columns: 1fr;
        }

        .sidebar {
          border-right: 0;
          border-bottom: 1px solid rgba(215, 222, 243, 0.9);
        }

        .section-grid,
        .diagram-layout {
          grid-template-columns: 1fr;
        }
      }

      @media (max-width: 720px) {
        .shell {
          padding: 12px;
        }

        .topbar,
        .sidebar,
        .content {
          padding: 16px;
        }

        .panel,
        .result-shell,
        .hero {
          border-radius: 22px;
        }

        .actions,
        .download-actions {
          flex-direction: column;
        }

        button {
          width: 100%;
        }

        .hero h3 {
          font-size: 24px;
        }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <div class="frame">
        <div class="topbar">
          <div class="brand">
            <div class="brand-badge">EA</div>
            <div class="brand-copy">
              <h1>Enterprise Architecture Agent</h1>
              <p>Generate a structured architecture brief with a downloadable draw.io diagram.</p>
            </div>
          </div>
          <div class="status">Service workspace ready</div>
        </div>

        <div class="workspace">
          <aside class="sidebar">
            <div class="panel">
              <h2>Brief</h2>
              <p class="panel-copy">
                Enter the architecture prompt on the left, generate the solution, and review the formatted output plus
                the rendered diagram on the right.
              </p>

              <form id="analyze-form">
                <div class="field">
                  <label for="cloud-provider">Preferred Cloud</label>
                  <select id="cloud-provider" name="cloud_provider">
                    <option value="">Auto-detect (default to Azure)</option>
                    <option value="Azure">Azure</option>
                    <option value="AWS">AWS</option>
                    <option value="GCP">GCP</option>
                    <option value="Hybrid / Multi-cloud">Hybrid / Multi-cloud</option>
                  </select>
                  <div class="hint">
                    Pick a cloud if you want the architecture and service suggestions biased to that environment.
                  </div>
                </div>

                <div class="field">
                  <label for="prompt">Architecture Prompt</label>
                  <textarea
                    id="prompt"
                    name="prompt"
                    placeholder="Design a target architecture for a global retailer using AEM, Adobe Commerce, SAP S/4HANA, Salesforce, and Azure API Management. Include integrations, security, non-functional requirements, and a phased roadmap."
                    required
                  ></textarea>
                  <div class="hint">
                    Include platforms, integration expectations, constraints, target users, or delivery goals. The API
                    will return the narrative plus downloadable draw.io and PPTX artifacts.
                  </div>
                </div>

                <div class="actions">
                  <button id="generate-btn" class="primary" type="submit">Generate</button>
                  <button id="reset-btn" class="secondary" type="button">Reset</button>
                </div>
              </form>

              <div id="form-message" class="message" role="status" aria-live="polite"></div>
            </div>
          </aside>

          <main class="content">
            <section id="hero" class="hero">
              <div class="hero-card">
                <div class="hero-icon"></div>
                <h3>Turn a solution prompt into a formatted architecture package.</h3>
                <p>
                  The workspace will show sectioned recommendations followed by full-width previews of the generated
                  draw.io and PPTX diagrams with download actions.
                </p>
              </div>
            </section>

            <section id="result-shell" class="result-shell" aria-live="polite">
              <div class="result-head">
                <div>
                  <p class="eyebrow">Generated Workspace</p>
                  <h3>Architecture recommendation</h3>
                  <p id="result-subtitle">Review the structured output and export the assets below.</p>
                </div>
                <div class="download-actions">
                  <button id="download-report" class="secondary" type="button">Download Report</button>
                  <button id="download-drawio" class="secondary" type="button">Download Draw.io</button>
                  <button id="download-pptx" class="secondary" type="button">Download PPTX</button>
                </div>
              </div>

              <div id="section-grid" class="section-grid"></div>

              <div class="diagram-layout">
                <article class="diagram-card">
                  <h4>Draw.io Diagram Preview</h4>
                  <div id="diagram-stage" class="diagram-stage"></div>
                  <div class="inline-note">
                    This preview is rendered directly from the generated draw.io XML returned by the API so the full
                    architecture stays visible in-browser before download.
                  </div>
                </article>

                <article class="diagram-card">
                  <h4>PPTX Deck Slide Preview</h4>
                  <div id="pptx-stage" class="diagram-stage"></div>
                  <div class="inline-note">
                    The slide preview reflects the generated PowerPoint deck artifact so you can review the presentation
                    layout before downloading the `.pptx` file.
                  </div>
                </article>
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>

    <script>
      const form = document.getElementById('analyze-form');
      const promptField = document.getElementById('prompt');
      const cloudProviderField = document.getElementById('cloud-provider');
      const generateBtn = document.getElementById('generate-btn');
      const resetBtn = document.getElementById('reset-btn');
      const hero = document.getElementById('hero');
      const resultShell = document.getElementById('result-shell');
      const sectionGrid = document.getElementById('section-grid');
      const diagramStage = document.getElementById('diagram-stage');
      const pptxStage = document.getElementById('pptx-stage');
      const formMessage = document.getElementById('form-message');
      const downloadReportBtn = document.getElementById('download-report');
      const downloadDrawioBtn = document.getElementById('download-drawio');
      const downloadPptxBtn = document.getElementById('download-pptx');

      let latestResponse = null;
      const SECTION_DEFINITIONS = [
        { title: 'Business Context', aliases: ['Business Context'] },
        { title: 'Architecture Overview', aliases: ['Architecture Overview', 'Target Architecture Overview'] },
        { title: 'Core Systems', aliases: ['Core Systems', 'Key Systems', 'Platform Components'] },
        { title: 'Integration Patterns', aliases: ['Integration Patterns', 'Integration Architecture'] },
        { title: 'Security & Identity', aliases: ['Security & Identity', 'Security and Identity', 'Identity & Security'] },
        { title: 'Data Flow', aliases: ['Data Flow', 'Data Architecture', 'Information Flow'] },
        { title: 'Non-Functional Requirements', aliases: ['Non-Functional Requirements', 'NFRs', 'Non Functional Requirements'] },
        { title: 'Risks & Assumptions', aliases: ['Risks & Assumptions', 'Risks and Assumptions'] },
        { title: 'Recommended Delivery Phases', aliases: ['Recommended Delivery Phases', 'Delivery Phases', 'Recommended Roadmap', 'Implementation Phases'] },
      ];

      const escapeHtml = (value) =>
        (value || '')
          .replaceAll('&', '&amp;')
          .replaceAll('<', '&lt;')
          .replaceAll('>', '&gt;')
          .replaceAll('"', '&quot;')
          .replaceAll("'", '&#39;');

      const stripHtml = (value) =>
        (value || '')
          .replace(/<br\\s*\\/?>/gi, '\\n')
          .replace(/<[^>]+>/g, '')
          .replace(/&nbsp;/g, ' ')
          .trim();

      const showMessage = (text, tone) => {
        formMessage.textContent = text;
        formMessage.className = 'message visible ' + tone;
      };

      const hideMessage = () => {
        formMessage.textContent = '';
        formMessage.className = 'message';
      };

      const setLoading = (loading) => {
        generateBtn.disabled = loading;
        generateBtn.textContent = loading ? 'Generating...' : 'Generate';
      };

      const escapeRegex = (value) => value.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');

      const normalizeHeadingLine = (value) =>
        (value || '')
          .replace(/\\*\\*/g, '')
          .replace(/^#{1,6}\\s*/, '')
          .replace(/^\\d+[.)]\\s*/, '')
          .trim();

      const matchSectionHeading = (line) => {
        const normalized = normalizeHeadingLine(line);
        for (const section of SECTION_DEFINITIONS) {
          for (const alias of section.aliases) {
            const pattern = new RegExp('^' + escapeRegex(alias) + '\\\\s*:?[\\\\s-]*(.*)$', 'i');
            const match = normalized.match(pattern);
            if (match) {
              return {
                title: section.title,
                remainder: (match[1] || '').trim(),
              };
            }
          }
        }
        return null;
      };

      const splitSections = (text) => {
        const normalized = (text || '').replace(/\\r/g, '').trim();
        if (!normalized) {
          return SECTION_DEFINITIONS.map((section) => ({ title: section.title, content: '' }));
        }

        const sectionsByTitle = new Map(SECTION_DEFINITIONS.map((section) => [section.title, []]));
        const lines = normalized.split('\\n');
        let currentTitle = null;

        lines.forEach((line, index) => {
          const headingMatch = matchSectionHeading(line.trim());
          if (headingMatch) {
            currentTitle = headingMatch.title;
            if (headingMatch.remainder) {
              sectionsByTitle.get(currentTitle).push(headingMatch.remainder);
            }
            return;
          }

          if (currentTitle) {
            sectionsByTitle.get(currentTitle).push(line);
            return;
          }

          if (index === 0 && line.trim()) {
            sectionsByTitle.get(SECTION_DEFINITIONS[0].title).push(line);
          }
        });

        return SECTION_DEFINITIONS.map((section) => ({
          title: section.title,
          content: (sectionsByTitle.get(section.title) || []).join('\\n').trim(),
        }));
      };

      const stripUiOnlyText = (content) =>
        (content || '')
          .replace(
            /If you want, I can turn this into a \\*\\*diagram-ready architecture blueprint\\*\\* with named boxes, flows, and layers for Visio\\/Miro\\/Lucidchart generation\\.?/gi,
            ''
          )
          .replace(/^#{0,3}\\s*(?:If you want|If you'd like|If you would like|If needed|Let me know if you'd like|I can also|I can next|Next, I can).*$/gim, '')
          .trim();

      const formatSectionLines = (content) => {
        const cleaned = stripUiOnlyText(content);
        const rawLines = cleaned
          .split('\\n')
          .map((line) => line.trim())
          .filter(Boolean);

        if (!rawLines.length) {
          return '<div class="detail-line">No details provided.</div>';
        }

        return rawLines
          .map((line) => {
            if (/^#{3,6}\\s+/.test(line)) {
              return '<div class="detail-subheading">' + escapeHtml(line.replace(/^#{3,6}\\s+/, '').trim()) + '</div>';
            }

            const isBullet = /^(?:[-*•]|\\d+\\.)\\s+/.test(line);
            const normalized = line.replace(/^(?:[-*•]|\\d+\\.)\\s+/, '').trim();
            const match = normalized.match(/^([^:]{1,80}):(\\s+.+)$/);
            const inlineHtml = (value) =>
              escapeHtml(value)
                .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/`([^`]+)`/g, '<code>$1</code>');

            if (match) {
              return (
                '<div class="detail-line' +
                (isBullet ? ' bullet' : '') +
                '"><strong>' +
                inlineHtml(match[1].trim() + ':') +
                '</strong> ' +
                inlineHtml(match[2].trim()) +
                '</div>'
              );
            }

            return '<div class="detail-line' + (isBullet ? ' bullet' : '') + '">' + inlineHtml(normalized) + '</div>';
          })
          .join('');
      };

      const renderSections = (data) => {
        const sections = splitSections(data.result);
        sectionGrid.innerHTML = sections
          .map(
            (section) =>
              '<article class="section-card"><div class="section-title">' +
              escapeHtml(section.title) +
              '</div><div class="section-lines">' +
              formatSectionLines(section.content) +
              '</div></article>'
          )
          .join('');
      };

      const parseStyle = (styleText) => {
        const result = {};
        (styleText || '')
          .split(';')
          .map((item) => item.trim())
          .filter(Boolean)
          .forEach((item) => {
            const [key, value] = item.split('=');
            if (key) {
              result[key] = value || '';
            }
          });
        return result;
      };

      const getGeometry = (cell) => {
        const geometry = cell.querySelector('mxGeometry');
        return {
          x: Number(geometry?.getAttribute('x') || 0),
          y: Number(geometry?.getAttribute('y') || 0),
          width: Number(geometry?.getAttribute('width') || 0),
          height: Number(geometry?.getAttribute('height') || 0),
        };
      };

      const renderDrawioPreview = (xml) => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(xml, 'text/xml');
        const mxGraphModel = doc.querySelector('mxGraphModel');
        const pageWidth = Number(mxGraphModel?.getAttribute('pageWidth') || 2700);
        const pageHeight = Number(mxGraphModel?.getAttribute('pageHeight') || 1450);
        const cells = Array.from(doc.querySelectorAll('mxCell'));
        const groups = new Map();
        const cellsById = new Map();
        const nodeBodies = [];
        const nodeDetails = new Map();
        const titles = new Map();
        const edges = [];

        cells.forEach((cell) => {
          const id = cell.getAttribute('id');
          if (id) {
            cellsById.set(id, cell);
          }

          if (cell.getAttribute('vertex') === '1' && (cell.getAttribute('style') || '').includes('group')) {
            groups.set(id, getGeometry(cell));
          }
        });

        cells.forEach((cell) => {
          const id = cell.getAttribute('id') || '';
          const parent = cell.getAttribute('parent') || '';
          const style = parseStyle(cell.getAttribute('style') || '');

          if (cell.getAttribute('edge') === '1') {
            edges.push({
              source: cell.getAttribute('source') || '',
              target: cell.getAttribute('target') || '',
              label: stripHtml(cell.getAttribute('value') || ''),
              style,
            });
            return;
          }

          if (cell.getAttribute('vertex') !== '1') {
            return;
          }

          if (/^node-[A-Za-z0-9_]+$/.test(id)) {
            const geometry = getGeometry(cell);
            const parentGeometry = groups.get(parent);
            const absoluteGeometry = parentGeometry
              ? {
                  x: parentGeometry.x + geometry.x,
                  y: parentGeometry.y + geometry.y,
                  width: geometry.width || parentGeometry.width,
                  height: geometry.height || parentGeometry.height,
                }
              : geometry;

            nodeBodies.push({
              id,
              parent,
              geometry: absoluteGeometry,
              style,
              isActor: style.shape === 'umlActor',
            });
            return;
          }

          if (/^node-[A-Za-z0-9_]+-title$/.test(id) || /^node-[A-Za-z0-9_]+-label$/.test(id)) {
            const key = id.replace(/-(title|label)$/, '');
            titles.set(key, stripHtml(cell.getAttribute('value') || ''));
            return;
          }

          if (/^node-[A-Za-z0-9_]+-detail-\\d+$/.test(id)) {
            const key = id.replace(/-detail-\\d+$/, '');
            const current = nodeDetails.get(key) || [];
            current.push(stripHtml(cell.getAttribute('value') || ''));
            nodeDetails.set(key, current);
          }
        });

        const nodeMap = new Map(
          nodeBodies.map((node) => [
            node.id,
            {
              ...node,
              title: titles.get(node.id) || stripHtml(cellsById.get(node.id)?.getAttribute('value') || node.id.replace(/^node-/, '')),
              details: nodeDetails.get(node.id) || [],
            },
          ])
        );

        const anchorPoint = (node, axisX, axisY) => ({
          x: node.geometry.x + node.geometry.width * axisX,
          y: node.geometry.y + node.geometry.height * axisY,
        });

        const orthogonalPath = (start, end) => {
          const horizontalGap = Math.abs(end.x - start.x);
          const verticalGap = Math.abs(end.y - start.y);
          if (horizontalGap > verticalGap) {
            const midX = start.x + (end.x - start.x) / 2;
            return `M ${start.x} ${start.y} L ${midX} ${start.y} L ${midX} ${end.y} L ${end.x} ${end.y}`;
          }
          const midY = start.y + (end.y - start.y) / 2;
          return `M ${start.x} ${start.y} L ${start.x} ${midY} L ${end.x} ${midY} L ${end.x} ${end.y}`;
        };

        const svgParts = [];
        svgParts.push(
          '<svg viewBox="0 0 ' +
            pageWidth +
            ' ' +
            pageHeight +
            '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Generated architecture diagram">'
        );
        svgParts.push(
          '<defs><marker id="arrowhead" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="#5b6478"></path></marker></defs>'
        );
        svgParts.push('<rect x="0" y="0" width="' + pageWidth + '" height="' + pageHeight + '" fill="#f8fbff"></rect>');

        edges.forEach((edge) => {
          const source = nodeMap.get(edge.source);
          const target = nodeMap.get(edge.target);
          if (!source || !target) {
            return;
          }

          const exitX = Number(edge.style.exitX || 0.5);
          const exitY = Number(edge.style.exitY || 0.5);
          const entryX = Number(edge.style.entryX || 0.5);
          const entryY = Number(edge.style.entryY || 0.5);
          const start = anchorPoint(source, exitX, exitY);
          const end = anchorPoint(target, entryX, entryY);
          const midX = (start.x + end.x) / 2;
          const midY = (start.y + end.y) / 2;
          const dash = edge.style.dashed === '1' ? ' stroke-dasharray="12 8"' : '';
          const path = orthogonalPath(start, end);

          svgParts.push(
            '<path d="' +
              path +
              '" fill="none" stroke="#5b6478" stroke-width="3"' +
              dash +
              ' marker-end="url(#arrowhead)"></path>'
          );

          if (edge.label) {
            svgParts.push(
              '<rect x="' +
                (midX - 92) +
                '" y="' +
                (midY - 16) +
                '" width="184" height="32" rx="12" fill="rgba(255,255,255,0.92)"></rect>'
            );
            svgParts.push(
              '<text x="' +
                midX +
                '" y="' +
                (midY + 5) +
                '" text-anchor="middle" font-size="22" font-family="Segoe UI, Arial, sans-serif" fill="#334155">' +
                escapeHtml(edge.label) +
                '</text>'
            );
          }
        });

        nodeBodies.forEach((node) => {
          const fill = node.style.fillColor || '#ffffff';
          const stroke = node.style.strokeColor || '#64748b';
          const title = escapeHtml(nodeMap.get(node.id)?.title || '');
          const details = nodeMap.get(node.id)?.details || [];
          const x = node.geometry.x;
          const y = node.geometry.y;
          const width = node.geometry.width;
          const height = node.geometry.height;

          if (node.isActor) {
            svgParts.push('<circle cx="' + (x + width / 2) + '" cy="' + (y + 18) + '" r="16" fill="#ffffff" stroke="' + stroke + '" stroke-width="3"></circle>');
            svgParts.push('<line x1="' + (x + width / 2) + '" y1="' + (y + 34) + '" x2="' + (x + width / 2) + '" y2="' + (y + 66) + '" stroke="' + stroke + '" stroke-width="3"></line>');
            svgParts.push('<line x1="' + (x + 5) + '" y1="' + (y + 46) + '" x2="' + (x + width - 5) + '" y2="' + (y + 46) + '" stroke="' + stroke + '" stroke-width="3"></line>');
            svgParts.push('<line x1="' + (x + width / 2) + '" y1="' + (y + 66) + '" x2="' + (x + 8) + '" y2="' + (y + height) + '" stroke="' + stroke + '" stroke-width="3"></line>');
            svgParts.push('<line x1="' + (x + width / 2) + '" y1="' + (y + 66) + '" x2="' + (x + width - 8) + '" y2="' + (y + height) + '" stroke="' + stroke + '" stroke-width="3"></line>');
            svgParts.push(
              '<text x="' +
                (x + width / 2) +
                '" y="' +
                (y + height + 34) +
                '" text-anchor="middle" font-size="24" font-weight="700" font-family="Segoe UI, Arial, sans-serif" fill="#0f172a">' +
                title +
                '</text>'
            );
            return;
          }

          svgParts.push(
            '<rect x="' +
              x +
              '" y="' +
              y +
              '" width="' +
              width +
              '" height="' +
              height +
              '" rx="18" fill="' +
              fill +
              '" stroke="' +
              stroke +
              '" stroke-width="3"></rect>'
          );
          svgParts.push(
            '<text x="' +
              (x + width / 2) +
              '" y="' +
              (y + 30) +
              '" text-anchor="middle" font-size="24" font-weight="700" font-family="Segoe UI, Arial, sans-serif" fill="#0f172a">' +
              title +
              '</text>'
          );

          details.slice(0, 6).forEach((detail, index) => {
            const column = index % 2;
            const row = Math.floor(index / 2);
            const tileWidth = (width - 30) / 2;
            const tileHeight = 28;
            const tileX = x + 10 + column * (tileWidth + 10);
            const tileY = y + 42 + row * 36;
            svgParts.push(
              '<rect x="' +
                tileX +
                '" y="' +
                tileY +
                '" width="' +
                tileWidth +
                '" height="' +
                tileHeight +
                '" rx="10" fill="rgba(255,255,255,0.42)"></rect>'
            );
            svgParts.push(
              '<text x="' +
                (tileX + tileWidth / 2) +
                '" y="' +
                (tileY + 19) +
                '" text-anchor="middle" font-size="14" font-family="Segoe UI, Arial, sans-serif" fill="#1f2937">' +
                escapeHtml(detail) +
                '</text>'
            );
          });
        });

        svgParts.push('</svg>');
        diagramStage.innerHTML = svgParts.join('');
      };

      const buildReport = (data) => {
        const sections = splitSections(data.result);
        const lines = [];
        lines.push('# Enterprise Architecture Recommendation');
        lines.push('');
        lines.push('Prompt:');
        lines.push(promptField.value.trim());
        lines.push('');
        lines.push('Cloud Provider:');
        lines.push(data.cloud_provider || 'Azure');
        lines.push('');
        lines.push('Detected Domains:');
        lines.push(data.detected_domains || 'Not provided');
        lines.push('');
        lines.push('Tools and Technologies:');
        if ((data.tools_and_technologies || []).length) {
          data.tools_and_technologies.forEach((item) => lines.push('- ' + item));
        } else {
          lines.push('- None');
        }
        lines.push('');
        lines.push('Suggested Cloud Services:');
        (data.suggested_azure_services || []).forEach((item) => lines.push('- ' + item));
        lines.push('');
        lines.push('Reusable Patterns:');
        if ((data.reusable_patterns || []).length) {
          data.reusable_patterns.forEach((item) => lines.push('- ' + item));
        } else {
          lines.push('- None');
        }
        lines.push('');
        lines.push('Prior Recommendations:');
        if ((data.prior_recommendations || []).length) {
          data.prior_recommendations.forEach((item) => lines.push('- ' + item));
        } else {
          lines.push('- None');
        }
        lines.push('');

        sections.forEach((section, index) => {
          lines.push((index + 1) + '. ' + section.title);
          lines.push(section.content || 'No details provided.');
          lines.push('');
        });

        return lines.join('\\n').trim() + '\\n';
      };

      const downloadFile = (filename, content, type) => {
        const blob = new Blob([content], { type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      };

      const downloadBase64File = (filename, base64Content, type) => {
        const binary = atob(base64Content || '');
        const bytes = new Uint8Array(binary.length);
        for (let index = 0; index < binary.length; index += 1) {
          bytes[index] = binary.charCodeAt(index);
        }
        const blob = new Blob([bytes], { type });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      };

      const renderResponse = (data) => {
        latestResponse = data;
        hero.style.display = 'none';
        resultShell.classList.add('visible');
        const subtitle = document.getElementById('result-subtitle');
        subtitle.textContent = 'Review the structured output and export the assets below. Cloud: ' + (data.cloud_provider || 'Azure') + '.';
        renderSections(data);
        renderDrawioPreview(data.drawio_xml || '');
        pptxStage.innerHTML = data.pptx_preview_svg || '';
      };

      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const prompt = promptField.value.trim();
        if (prompt.length < 10) {
          showMessage('Please enter a longer architecture prompt so the agent has enough context.', 'error');
          return;
        }

        hideMessage();
        setLoading(true);

        try {
          const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, cloud_provider: cloudProviderField.value || null }),
          });

          if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || 'Architecture analysis failed.');
          }

          const payload = await response.json();
          renderResponse(payload);
          showMessage('Architecture package generated successfully.', 'success');
        } catch (error) {
          showMessage(error.message || 'Unable to generate the architecture package.', 'error');
        } finally {
          setLoading(false);
        }
      });

      resetBtn.addEventListener('click', () => {
        form.reset();
        cloudProviderField.value = '';
        latestResponse = null;
        hideMessage();
        resultShell.classList.remove('visible');
        hero.style.display = 'grid';
        sectionGrid.innerHTML = '';
        diagramStage.innerHTML = '';
        pptxStage.innerHTML = '';
      });

      downloadReportBtn.addEventListener('click', () => {
        if (!latestResponse) {
          showMessage('Generate an architecture package before downloading the report.', 'error');
          return;
        }
        downloadFile('enterprise-architecture-report.md', buildReport(latestResponse), 'text/markdown;charset=utf-8');
      });

      downloadDrawioBtn.addEventListener('click', () => {
        if (!latestResponse) {
          showMessage('Generate an architecture package before downloading the draw.io diagram.', 'error');
          return;
        }
        downloadFile('enterprise-architecture.drawio', latestResponse.drawio_xml || '', 'application/xml;charset=utf-8');
      });

      downloadPptxBtn.addEventListener('click', () => {
        if (!latestResponse) {
          showMessage('Generate an architecture package before downloading the PowerPoint deck.', 'error');
          return;
        }
        downloadBase64File(
          'enterprise-architecture-deck.pptx',
          latestResponse.pptx_base64 || '',
          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        );
      });
    </script>
  </body>
</html>
"""
