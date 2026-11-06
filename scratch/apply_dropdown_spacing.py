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

old_hero_actions = """.hero-actions {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 16px;
      margin-bottom: 36px;
    }

    /* Shield Badges */
    .shields {
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 18px 28px;
    }"""

new_hero_actions = """.hero-actions {
      position: relative;
      z-index: 50;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 16px;
      margin-bottom: 40px;
    }

    /* Shield Badges */
    .shields {
      position: relative;
      z-index: 1;
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 18px 28px;
    }"""

old_dropdown_css_start = "/* ============================================================\n       RELEASES / UPDATES DROPDOWN & VERSION SELECTOR\n       ============================================================ */"
old_dropdown_css_end = "/* ============================================================\n       UPDATES & CHANGELOG SECTION"

new_dropdown_css = """/* ============================================================
       RELEASES / UPDATES DROPDOWN & VERSION SELECTOR
       ============================================================ */
    .rel-dropdown-wrapper {
      position: relative;
      display: inline-block;
      z-index: 100;
    }

    .rel-toggle-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      font-size: 13.5px;
      font-weight: 700;
      padding: 14px 22px;
      border-radius: 14px;
    }

    .rel-dropdown-menu {
      position: absolute;
      top: calc(100% + 14px);
      left: 0;
      width: 490px;
      max-width: min(490px, calc(100vw - 32px));
      background: #0e0e11;
      border: 1.5px solid rgba(255, 255, 255, 0.16);
      border-radius: 22px;
      box-shadow: 0 25px 65px rgba(0, 0, 0, 0.9), 0 0 0 1px rgba(255, 255, 255, 0.08);
      padding: 22px 22px 20px 22px;
      z-index: 99999;
      display: none;
      opacity: 0;
      transform: translateY(-8px);
      transition: opacity .2s var(--ease), transform .2s var(--ease);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
    }

    .rel-dropdown-menu.is-open {
      display: block;
      opacity: 1;
      transform: translateY(0);
    }

    .rel-dropdown-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 14px;
      margin-bottom: 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .rel-head-title {
      font-size: 12.5px;
      font-weight: 800;
      color: var(--paper);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .rel-head-badge {
      font-size: 11px;
      font-weight: 600;
      color: var(--muted-d);
      background: var(--ink-3);
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid var(--ink-line);
    }

    .rel-list-container {
      display: flex;
      flex-direction: column;
      gap: 14px;
      max-height: 420px;
      overflow-y: auto;
      padding-right: 6px;
      overscroll-behavior: contain;
    }

    .rel-list-container::-webkit-scrollbar {
      width: 6px;
    }

    .rel-list-container::-webkit-scrollbar-track {
      background: transparent;
    }

    .rel-list-container::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.22);
      border-radius: 4px;
    }

    .rel-list-container::-webkit-scrollbar-thumb:hover {
      background: var(--gold);
    }

    .rel-item {
      background: #141418;
      border: 1.5px solid rgba(255, 255, 255, 0.12);
      border-radius: 16px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: border-color .2s var(--ease), background .2s var(--ease), transform .2s var(--ease);
    }

    .rel-item:hover {
      border-color: var(--gold);
      background: #1a1a20;
      transform: translateY(-1px);
    }

    .rel-item.is-latest {
      border-color: rgba(245, 184, 46, 0.65);
      background: linear-gradient(145deg, #181714 0%, #13171b 100%);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 25px rgba(245, 184, 46, 0.09);
    }

    .rel-item-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 2px;
    }

    .rel-ver-tag {
      font-family: var(--font-mono, monospace);
      font-size: 14px;
      font-weight: 800;
      color: var(--paper);
      letter-spacing: -0.01em;
    }

    .rel-status-badge {
      font-size: 10.5px;
      font-weight: 800;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 5px;
      letter-spacing: 0.04em;
    }

    .rel-status-badge.badge-latest {
      background: var(--gold);
      color: #0b0b0b;
    }

    .rel-status-badge.badge-older {
      background: var(--ink-3);
      color: var(--muted-d);
      border: 1px solid var(--ink-line);
    }

    .rel-item-title {
      font-size: 13.5px;
      font-weight: 700;
      color: var(--paper);
      line-height: 1.4;
      margin: 0;
    }

    .rel-item-meta {
      font-size: 11.5px;
      color: var(--muted-d);
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 2px 0;
    }

    .rel-item-notes {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.72);
      line-height: 1.5;
      margin: 0;
    }

    .rel-item-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 4px;
      padding-top: 12px;
      border-top: 1px dashed rgba(255, 255, 255, 0.12);
    }

    .rel-size {
      font-size: 11px;
      color: var(--muted-d);
      font-weight: 600;
    }

    .rel-dl-link {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11.5px;
      font-weight: 700;
      color: #0b0b0b;
      background: var(--gold);
      padding: 6px 14px;
      border-radius: 8px;
      text-decoration: none;
      transition: filter .15s var(--ease), transform .15s var(--ease);
      white-space: nowrap;
    }

    .rel-dl-link:hover {
      filter: brightness(1.12);
      transform: translateY(-1px);
    }

    .rel-dl-link.link-older {
      background: var(--ink-3);
      color: var(--paper);
      border: 1px solid var(--ink-line);
    }

    .rel-dl-link.link-older:hover {
      background: var(--paper);
      color: #0b0b0b;
    }

    """

old_js_behavior = """    // Dropdown toggle & click outside behavior
    const btnToggleReleases = document.getElementById('btnToggleReleases');
    const relDropdownMenu = document.getElementById('relDropdownMenu');
    if (btnToggleReleases && relDropdownMenu) {
      btnToggleReleases.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = relDropdownMenu.classList.toggle('is-open');
        btnToggleReleases.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });

      document.addEventListener('click', (e) => {
        if (!relDropdownMenu.contains(e.target) && e.target !== btnToggleReleases) {
          relDropdownMenu.classList.remove('is-open');
          btnToggleReleases.setAttribute('aria-expanded', 'false');
        }
      });
    }"""

new_js_behavior = """    // Dropdown toggle & click outside behavior with auto-alignment
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
    }"""

for fpath in html_files:
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update hero actions
    if old_hero_actions in content:
        content = content.replace(old_hero_actions, new_hero_actions)
    else:
        print(f"Warning: old_hero_actions not found in {fpath}")

    # 2. Update dropdown CSS
    p1 = content.find(old_dropdown_css_start)
    p2 = content.find(old_dropdown_css_end)
    if p1 != -1 and p2 != -1:
        content = content[:p1] + new_dropdown_css + content[p2:]
    else:
        print(f"Warning: dropdown css markers not found in {fpath}")

    # 3. Update JS behavior
    if old_js_behavior in content:
        content = content.replace(old_js_behavior, new_js_behavior)
    else:
        print(f"Warning: old_js_behavior not found in {fpath}")

    with open(fpath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)
    print(f"[OK] Updated HTML: {fpath}")

for fpath in py_files:
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    if old_hero_actions in content:
        content = content.replace(old_hero_actions, new_hero_actions)
    else:
        print(f"Warning: old_hero_actions not found in {fpath}")

    p1 = content.find(old_dropdown_css_start)
    p2 = content.find(old_dropdown_css_end)
    if p1 != -1 and p2 != -1:
        content = content[:p1] + new_dropdown_css + content[p2:]
    else:
        print(f"Warning: dropdown css markers not found in {fpath}")

    if old_js_behavior in content:
        content = content.replace(old_js_behavior, new_js_behavior)
    else:
        print(f"Warning: old_js_behavior not found in {fpath}")

    with open(fpath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)
    print(f"[OK] Updated PY: {fpath}")

print("All files updated successfully!")
