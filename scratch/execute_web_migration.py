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

# 1. CSS to replace
css_start = "/* ============================================================\n       RELEASES / UPDATES DROPDOWN & VERSION SELECTOR\n       ============================================================ */"
css_end = "/* ============================================================\n       RESPONSIVE BREAKPOINTS\n       ============================================================ */"

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

# 2. Hero actions snippet
old_hero_actions = """        <div class="hero-actions reveal">
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

new_hero_actions = """        <div class="hero-actions reveal">
          <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-gold btn-download-latest" data-download-link="latest">
            <span>Download Windows Setup (<span class="dyn-latest-ver">v2.2.0</span>)</span>
            <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
          </a>

          <a href="#older-versions" class="btn btn-line" title="View all previous builds and changelog archive">
            <span>Older Versions &amp; Archive &darr;</span>
          </a>

          <a href="#inspector" class="btn btn-line">
            <span>Test Stream Analyzer</span>
            <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
          </a>
        </div>"""

# 3. Formats section older versions container insertion
old_formats_end = """        <!-- Card 4: Lossless M4A & FLAC -->
        <div class="c-card reveal" data-cat="audio">
          <div>
            <div class="c-top">
              <span class="c-pill">Lossless Master</span>
              <div class="c-icon"><svg class="ic"><use href="#i-bolt"></use></svg></div>
            </div>
            <h3>Lossless M4A &amp; Opus Pure Audio</h3>
            <p>Direct copy extraction from YouTube's highest quality audio stream without re-compression. Ideal for audiophiles and DAWs.</p>
          </div>
          <div>
            <div class="c-specs-mini">
              <span>Zero Re-encoding</span>
              <span>Bit-for-Bit Copy</span>
            </div>
            <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-line btn-sm" style="width: 100%;">
              <span>Download Master Tool</span>
              <svg class="ic"><use href="#i-download"></use></svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>"""

new_formats_end = """        <!-- Card 4: Lossless M4A & FLAC -->
        <div class="c-card reveal" data-cat="audio">
          <div>
            <div class="c-top">
              <span class="c-pill">Lossless Master</span>
              <div class="c-icon"><svg class="ic"><use href="#i-bolt"></use></svg></div>
            </div>
            <h3>Lossless M4A &amp; Opus Pure Audio</h3>
            <p>Direct copy extraction from YouTube's highest quality audio stream without re-compression. Ideal for audiophiles and DAWs.</p>
          </div>
          <div>
            <div class="c-specs-mini">
              <span>Zero Re-encoding</span>
              <span>Bit-for-Bit Copy</span>
            </div>
            <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-line btn-sm" style="width: 100%;">
              <span>Download Master Tool</span>
              <svg class="ic"><use href="#i-download"></use></svg>
            </a>
          </div>
        </div>
      </div>

      <!-- ============================================================
           OLDER VERSIONS & PREVIOUS BUILDS ARCHIVE
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

# 4. Old updates section removal
old_updates_section = """  <!-- ============================================================
       RELEASE UPDATES & CHANGELOG
       ============================================================ -->
  <section class="section updates-sec" id="updates" aria-labelledby="up-title">
    <div class="wrap">
      <div class="sec-head">
        <div>
          <p class="sticker reveal"><span>Release History</span></p>
          <h2 class="reveal" id="up-title">
            <span>Updates &amp;</span>
            <mark>Changelog.</mark>
          </h2>
        </div>
        <p class="sec-note reveal">
          Every new release uploaded to Google Drive automatically becomes the latest version for all download buttons. Older versions are preserved below with their release dates so you can download any previous build anytime.
        </p>
      </div>

      <div class="updates-timeline" id="sectionUpdatesList">
        <!-- Rendered dynamically from APP_RELEASES -->
      </div>
    </div>
  </section>

"""

# 5. Nav link update
old_nav_link = '<a href="#updates">Updates</a>'
new_nav_link = '<a href="#older-versions">Older Versions</a>'

# 6. JavaScript logic update
old_js_start = "      // 3. Render Hero Dropdown List"
old_js_end = "    // Dropdown toggle & click outside behavior with auto-alignment"

new_js = """      // 3. Render Older Versions Cards in the Formats Archive Section
      const ovContainer = document.getElementById('olderVersionsList');
      if (ovContainer) {
        const olderReleases = releases.filter(r => !r.is_latest && r.version !== latest.version);
        if (olderReleases.length === 0) {
          ovContainer.innerHTML = `
            <div style="text-align:center; padding: 24px; color: var(--muted-d); font-size: 13.5px;">
              All download buttons are delivering the latest flagship release (${latest.version}). No older releases are archived yet.
            </div>
          `;
        } else {
          ovContainer.innerHTML = olderReleases.map(rel => `
            <div class="ov-card reveal">
              <div class="ov-card-info">
                <div class="ov-card-meta">
                  <span class="ov-ver-tag">${rel.version}</span>
                  <span class="ov-badge-status">Preserved Release</span>
                  <span class="ov-date">📅 Released: ${rel.date_formatted || rel.date}</span>
                  <span class="ov-size">📦 ${rel.size || 'Installer'}</span>
                </div>
                <h4 class="ov-card-title">${rel.title}</h4>
                <p class="ov-card-notes">${rel.notes || ''}</p>
              </div>
              <div class="ov-card-action">
                <a href="${rel.url}" target="_blank" rel="noopener noreferrer" class="btn btn-line btn-sm" data-download-specific-version="${rel.version}">
                  <span>Download ${rel.version}</span>
                  <svg class="ic"><use href="#i-download"></use></svg>
                </a>
              </div>
            </div>
          `).join('');
        }
      }
    }

"""

old_toggle_js = """    // Dropdown toggle & click outside behavior with auto-alignment
    const btnToggleReleases = document.getElementById('btnToggleReleases');
    const relDropdownMenu = document.getElementById('relDropdownMenu');
    if (btnToggleReleases && relDropdownMenu) {
      btnToggleReleases.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = relDropdownMenu.classList.toggle('is-open');
        btnToggleReleases.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        if (isOpen) {
          const rect = relDropdownMenu.getBoundingClientRect();
          if (rect.right > window.innerWidth - 16) {
            relDropdownMenu.style.left = 'auto';
            relDropdownMenu.style.right = '0';
          } else {
            relDropdownMenu.style.left = '0';
            relDropdownMenu.style.right = 'auto';
          }
        }
      });

      document.addEventListener('click', (e) => {
        if (!relDropdownMenu.contains(e.target) && e.target !== btnToggleReleases) {
          relDropdownMenu.classList.remove('is-open');
          btnToggleReleases.setAttribute('aria-expanded', 'false');
        }
      });
    }

"""

def update_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # CSS replacement
    p1 = text.find(css_start)
    p2 = text.find(css_end)
    if p1 != -1 and p2 != -1:
        text = text[:p1] + new_older_versions_css + text[p2:]
    else:
        print(f"Warning: CSS markers not found in {filepath}")

    # Hero actions replacement
    if old_hero_actions in text:
        text = text.replace(old_hero_actions, new_hero_actions)
    else:
        print(f"Warning: old_hero_actions not found in {filepath}")

    # Formats section replacement
    if old_formats_end in text:
        text = text.replace(old_formats_end, new_formats_end)
    else:
        print(f"Warning: old_formats_end not found in {filepath}")

    # Old updates section removal
    if old_updates_section in text:
        text = text.replace(old_updates_section, "")
    else:
        print(f"Warning: old_updates_section not found in {filepath}")

    # Nav link replacement
    if old_nav_link in text:
        text = text.replace(old_nav_link, new_nav_link)

    # JS replacement
    p_js1 = text.find(old_js_start)
    p_js2 = text.find(old_js_end)
    if p_js1 != -1 and p_js2 != -1:
        text = text[:p_js1] + new_js + text[p_js2:]
    else:
        print(f"Warning: JS markers not found in {filepath}")

    if old_toggle_js in text:
        text = text.replace(old_toggle_js, "")

    with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(text)
    print(f"[OK] Migrated {filepath}")

for f in html_files + py_files:
    update_file(f)

print("Migration completed across all files!")
