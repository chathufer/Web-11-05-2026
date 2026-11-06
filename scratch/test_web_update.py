import os

base_dir = r"c:\Users\Chathufer\Downloads\Youtube video dowonloader"

html_files = [
    os.path.join(base_dir, "index.html"),
    os.path.join(base_dir, "public", "index.html"),
    os.path.join(base_dir, "deploy_vercel", "index.html"),
    os.path.join(base_dir, "deploy_vercel", "public", "index.html"),
]

py_files = [
    os.path.join(base_dir, "backend", "website_html.py"),
    os.path.join(base_dir, "deploy_vercel", "backend", "website_html.py"),
]

# 1. New CSS for Older Versions
new_older_versions_css = """/* ============================================================
       OLDER VERSIONS & PREVIOUS BUILDS ARCHIVE
       ============================================================ */
    .older-versions-sec {
      margin-top: 48px;
      padding: 36px 36px 32px 36px;
      background: var(--ink-2);
      border: 2px solid var(--ink-line);
      border-radius: 24px;
      box-shadow: 0 16px 45px rgba(0, 0, 0, 0.4);
    }

    .ov-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 20px;
      padding-bottom: 22px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--ink-line);
      flex-wrap: wrap;
    }

    .ov-head-left {
      max-width: 680px;
    }

    .ov-title {
      font-size: clamp(1.4rem, 1.2rem + 1vw, 1.85rem);
      font-weight: 800;
      color: var(--paper);
      margin: 10px 0 6px 0;
      letter-spacing: -0.02em;
    }

    .ov-desc {
      font-size: 13.5px;
      color: var(--muted-d);
      line-height: 1.55;
      margin: 0;
    }

    .ov-head-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(245, 184, 46, 0.1);
      border: 1px solid rgba(245, 184, 46, 0.35);
      color: var(--paper);
      padding: 8px 16px;
      border-radius: 100px;
      font-size: 12.5px;
      font-weight: 700;
      white-space: nowrap;
    }

    .ov-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #4ec9b0;
      box-shadow: 0 0 10px #4ec9b0;
      animation: pulseDot 2s infinite ease-in-out;
    }

    @keyframes pulseDot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    .ov-cards-list {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .ov-card {
      background: #141418;
      border: 1.5px solid rgba(255, 255, 255, 0.1);
      border-radius: 18px;
      padding: 22px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      transition: transform .2s var(--ease), border-color .2s var(--ease), background .2s var(--ease);
    }

    .ov-card:hover {
      border-color: var(--gold);
      background: #191920;
      transform: translateY(-2px);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
    }

    .ov-card-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .ov-card-meta {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }

    .ov-ver-tag {
      font-family: var(--font-mono, monospace);
      font-size: 15px;
      font-weight: 800;
      color: var(--paper);
    }

    .ov-badge-status {
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 5px;
      letter-spacing: 0.04em;
      background: var(--ink-3);
      color: var(--muted-d);
      border: 1px solid var(--ink-line);
    }

    .ov-date {
      font-size: 12px;
      color: var(--muted-d);
      font-weight: 600;
    }

    .ov-size {
      font-size: 11px;
      color: var(--muted-d);
      font-family: var(--font-mono, monospace);
      background: var(--ink-3);
      padding: 2px 8px;
      border-radius: 6px;
    }

    .ov-card-title {
      font-size: 14.5px;
      font-weight: 700;
      color: var(--paper);
      margin: 0;
    }

    .ov-card-notes {
      font-size: 12.5px;
      color: rgba(255, 255, 255, 0.72);
      line-height: 1.5;
      margin: 0;
    }

    .ov-card-action {
      flex-shrink: 0;
    }

    @media (max-width: 768px) {
      .older-versions-sec {
        padding: 24px 18px;
        margin-top: 36px;
      }
      .ov-card {
        flex-direction: column;
        align-items: stretch;
        padding: 20px 16px;
        gap: 16px;
      }
      .ov-card-action .btn {
        width: 100%;
        justify-content: center;
      }
    }
"""

# Old hero actions containing rel-dropdown-wrapper
old_hero_actions_snippet = """        <div class="hero-actions reveal">
          <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-gold btn-download-latest" data-download-link="latest">
            <span>Download Windows Setup (<span class="dyn-latest-ver">v2.2.0</span>)</span>
            <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
          </a>

          <!-- Releases & Updates Dropdown Trigger -->
          <div class="rel-dropdown-wrapper" id="heroRelDropdown">
            <button type="button" class="btn btn-line rel-toggle-btn" id="btnToggleReleases" aria-haspopup="true" aria-expanded="false" title="View Version History & Previous Releases">
              <span>▾ Updates &amp; Older Versions</span>
            </button>

            <!-- Dropdown Menu -->
            <div class="rel-dropdown-menu" id="relDropdownMenu" role="menu">
              <div class="rel-dropdown-head">
                <span class="rel-head-title">Release History</span>
                <span class="rel-head-badge">Google Drive</span>
              </div>
              <div class="rel-list-container" id="relListContainer">
                <!-- Dynamically populated from APP_RELEASES -->
              </div>
            </div>
          </div>

          <a href="#inspector" class="btn btn-line">
            <span>Test Stream Analyzer</span>
            <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
          </a>
        </div>"""

new_hero_actions_snippet = """        <div class="hero-actions reveal">
          <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-gold btn-download-latest" data-download-link="latest">
            <span>Download Windows Setup (<span class="dyn-latest-ver">v2.2.0</span>)</span>
            <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
          </a>

          <a href="#older-versions" class="btn btn-line" title="Scroll down to Older Versions Archive">
            <span>Older Versions &amp; Archive &darr;</span>
          </a>

          <a href="#inspector" class="btn btn-line">
            <span>Test Stream Analyzer</span>
            <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
          </a>
        </div>"""

# Older versions section to inject into the Formats / Pipelines section right under c-grid
older_versions_html = """      <!-- ============================================================
           OLDER VERSIONS & PREVIOUS BUILDS
           ============================================================ -->
      <div class="older-versions-sec reveal" id="older-versions">
        <div class="ov-head">
          <div class="ov-head-left">
            <span class="sticker"><span>Build Archive</span></span>
            <h3 class="ov-title">Older Versions</h3>
            <p class="ov-desc">
              Whenever a new update is released, the latest build becomes the default download across the site. All previous releases are preserved here with full changelogs and direct Google Drive download links.
            </p>
          </div>
          <div class="ov-head-badge">
            <span class="ov-dot"></span>
            <span>Current Latest: <strong class="dyn-latest-ver">v2.2.0</strong></span>
          </div>
        </div>

        <div class="ov-cards-list" id="olderVersionsList">
          <!-- Dynamically populated from APP_RELEASES -->
        </div>
      </div>
    </div>
  </section>"""

# Target to replace in formats section
target_cgrid_end = """        </div>
      </div>
    </div>
  </section>"""

replacement_cgrid_end = """        </div>
      </div>

""" + older_versions_html

# Old Updates section to remove / clean up
old_updates_sec_start = "  <!-- ============================================================\n       RELEASE UPDATES & CHANGELOG\n       ============================================================ -->\n  <section class=\"section updates-sec\" id=\"updates\" aria-labelledby=\"up-title\">"
old_updates_sec_end = "  </section>\n\n  <!-- ============================================================\n       PRICING / LICENSE PASSES"

new_pricing_start = "  <!-- ============================================================\n       PRICING / LICENSE PASSES"

print("Script template ready.")
