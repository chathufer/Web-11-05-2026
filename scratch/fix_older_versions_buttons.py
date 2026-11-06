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

# 1. Update CSS for ov-card and ov-dl-btn
css_target = ".ov-card {"
new_ov_css = """    .ov-card {
      opacity: 1 !important;
      visibility: visible !important;
      display: flex !important;
      background: #141418;
      border: 1.5px solid rgba(255, 255, 255, 0.12);
      border-radius: 18px;
      padding: 22px 26px;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      transition: transform .2s var(--ease), border-color .2s var(--ease), background .2s var(--ease);
    }

    .ov-dl-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--gold);
      color: #0b0b0b !important;
      font-weight: 800;
      font-size: 13.5px;
      padding: 10px 22px;
      border-radius: 10px;
      text-decoration: none;
      transition: filter .15s ease, transform .15s ease, box-shadow .15s ease;
      box-shadow: 0 4px 14px rgba(245, 184, 46, 0.25);
      white-space: nowrap;
    }

    .ov-dl-btn:hover {
      filter: brightness(1.15);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(245, 184, 46, 0.4);
    }

    .ov-dl-btn svg {
      width: 15px;
      height: 15px;
    }"""

# 2. Static pre-rendered cards
target_empty_container = """        <div class="ov-cards-list" id="olderVersionsList">
          <!-- Dynamically populated from APP_RELEASES -->
        </div>"""

pre_rendered_cards = """        <div class="ov-cards-list" id="olderVersionsList">
          <div class="ov-card">
            <div class="ov-card-info">
              <div class="ov-card-meta">
                <span class="ov-ver-tag">v2.2.0</span>
                <span class="ov-badge-status">Previous Version</span>
                <span class="ov-date">📅 Released: Nov 06, 2026</span>
                <span class="ov-size">📦 57.7 MB</span>
              </div>
              <h4 class="ov-card-title">Turbo Speed &amp; QuickJS Challenge Solver Engine</h4>
              <p class="ov-card-notes">Fixed YouTube CDN bandwidth throttling (50MB/s+ throughput), bundled lightweight QuickJS JS challenge runtime, 7-day trial recovery, completely silent launch without flashing CMD windows.</p>
            </div>
            <div class="ov-card-action">
              <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="ov-dl-btn" data-download-specific-version="v2.2.0">
                <span>Download v2.2.0 (57.7 MB)</span>
                <svg class="ic"><use href="#i-download"></use></svg>
              </a>
            </div>
          </div>

          <div class="ov-card">
            <div class="ov-card-info">
              <div class="ov-card-meta">
                <span class="ov-ver-tag">v2.1.0</span>
                <span class="ov-badge-status">Previous Version</span>
                <span class="ov-date">📅 Released: Nov 05, 2026</span>
                <span class="ov-size">📦 57.5 MB</span>
              </div>
              <h4 class="ov-card-title">Browse &amp; Search with In-Queue Quality Selector</h4>
              <p class="ov-card-notes">Added built-in YouTube Search &amp; Browse workstation, in-queue quality resolution picker dialog, 6 calm theme color palettes, and eliminated download progress UI flickering.</p>
            </div>
            <div class="ov-card-action">
              <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="ov-dl-btn" data-download-specific-version="v2.1.0">
                <span>Download v2.1.0 (57.5 MB)</span>
                <svg class="ic"><use href="#i-download"></use></svg>
              </a>
            </div>
          </div>

          <div class="ov-card">
            <div class="ov-card-info">
              <div class="ov-card-meta">
                <span class="ov-ver-tag">v2.0.0</span>
                <span class="ov-badge-status">Previous Version</span>
                <span class="ov-date">📅 Released: Nov 04, 2026</span>
                <span class="ov-size">📦 56.9 MB</span>
              </div>
              <h4 class="ov-card-title">Initial Commercial Studio Edition Launch</h4>
              <p class="ov-card-notes">Official release of Media Downloader Pro with 4K 60FPS video streams, TikTok watermark-free ripper, HWID cryptographic licensing, and high-compression single Windows installer.</p>
            </div>
            <div class="ov-card-action">
              <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="ov-dl-btn" data-download-specific-version="v2.0.0">
                <span>Download v2.0.0 (56.9 MB)</span>
                <svg class="ic"><use href="#i-download"></use></svg>
              </a>
            </div>
          </div>
        </div>"""

# 3. Dynamic JS render logic - without reveal and using ov-dl-btn
old_dynamic_js = """          ovContainer.innerHTML = olderReleases.map(rel => `
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
          `).join('');"""

new_dynamic_js = """          ovContainer.innerHTML = olderReleases.map(rel => `
            <div class="ov-card">
              <div class="ov-card-info">
                <div class="ov-card-meta">
                  <span class="ov-ver-tag">${rel.version}</span>
                  <span class="ov-badge-status">Previous Version</span>
                  <span class="ov-date">📅 Released: ${rel.date_formatted || rel.date}</span>
                  <span class="ov-size">📦 ${rel.size || 'Installer'}</span>
                </div>
                <h4 class="ov-card-title">${rel.title}</h4>
                <p class="ov-card-notes">${rel.notes || ''}</p>
              </div>
              <div class="ov-card-action">
                <a href="${rel.url}" target="_blank" rel="noopener noreferrer" class="ov-dl-btn" data-download-specific-version="${rel.version}">
                  <span>Download ${rel.version} (${rel.size || 'Setup'})</span>
                  <svg class="ic"><use href="#i-download"></use></svg>
                </a>
              </div>
            </div>
          `).join('');"""

# 4. Also add Older Versions shortcut button in Flagship 8K Card
old_flagship_actions = """            <div class="f-actions">
              <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-ink">
                <span>Download Setup v2.2</span>
                <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
              </a>
              <a href="#inspector" class="btn btn-line" style="border-color: var(--ink); color: var(--ink);">
                <span>Inspect 8K Stream</span>
                <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
              </a>
            </div>"""

new_flagship_actions = """            <div class="f-actions">
              <a href="https://drive.google.com/file/d/1oDrWH2SAtZK_gET-T9O9Ts0KX3Gcrsnc/view?usp=drive_link" target="_blank" rel="noopener noreferrer" class="btn btn-ink btn-download-latest" data-download-link="latest">
                <span>Download Setup (<span class="dyn-latest-ver">v2.3.0</span>)</span>
                <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
              </a>
              <a href="#older-versions" class="btn btn-line" style="border-color: var(--ink); color: var(--ink);">
                <span>Older Versions &darr;</span>
              </a>
              <a href="#inspector" class="btn btn-line" style="border-color: var(--ink); color: var(--ink);">
                <span>Inspect 8K Stream</span>
                <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
              </a>
            </div>"""

def process_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Pre-rendered cards injection
    if target_empty_container in content:
        content = content.replace(target_empty_container, pre_rendered_cards)
        print(f"[OK] Injected pre-rendered cards in {filepath}")
    else:
        print(f"[WARN] target_empty_container not found in {filepath}")

    # Dynamic JS replacement
    if old_dynamic_js in content:
        content = content.replace(old_dynamic_js, new_dynamic_js)
        print(f"[OK] Updated dynamic JS in {filepath}")
    else:
        print(f"[WARN] old_dynamic_js not found in {filepath}")

    # CSS update
    if ".ov-card {" in content and ".ov-dl-btn {" not in content:
        p_css1 = content.find(".ov-card {")
        p_css2 = content.find(".ov-card:hover {")
        if p_css1 != -1 and p_css2 != -1:
            content = content[:p_css1] + new_ov_css + "\n\n    " + content[p_css2:]
            print(f"[OK] Injected .ov-dl-btn CSS in {filepath}")

    # Flagship actions update
    if old_flagship_actions in content:
        content = content.replace(old_flagship_actions, new_flagship_actions)
        print(f"[OK] Added Older Versions button to 8K Flagship in {filepath}")

    with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)

for f in html_files + py_files:
    process_file(f)

print("Finished processing all files!")
