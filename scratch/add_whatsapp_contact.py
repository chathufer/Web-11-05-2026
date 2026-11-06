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

# 1. WhatsApp SVG Symbol
wa_symbol = """    <symbol id="i-whatsapp" viewBox="0 0 24 24"><path fill="currentColor" d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm.01 1.67c2.2 0 4.26.86 5.82 2.41a8.17 8.17 0 0 1 2.41 5.83c0 4.54-3.7 8.24-8.24 8.24-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.19 8.19 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24zm4.52 11.53c-.25-.13-1.47-.72-1.7-.81-.23-.08-.39-.13-.56.13-.17.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.13-1.06-.39-2.02-1.25-.75-.67-1.26-1.5-1.41-1.75-.14-.25-.02-.39.11-.51.11-.11.25-.29.38-.44.13-.14.17-.25.25-.42.08-.17.04-.31-.02-.44-.06-.13-.56-1.35-.77-1.85-.2-.49-.41-.42-.56-.43h-.48c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1s.9 2.43 1.03 2.6c.13.17 1.77 2.7 4.29 3.78.6.26 1.07.41 1.43.53.6.19 1.15.16 1.58.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.15-1.18-.06-.11-.23-.17-.48-.3z"/></symbol>
  </svg>"""

# 2. Contact & WhatsApp CSS
wa_css = """    /* ============================================================
       CONTACT & WHATSAPP BUYER GROUP SECTION
       ============================================================ */
    .contact-sec {
      background: var(--ink);
      border-top: 1px solid var(--ink-line);
      position: relative;
    }

    .wa-card {
      background: linear-gradient(145deg, #121316 0%, #0d1210 100%);
      border: 2px solid rgba(37, 211, 102, 0.35);
      border-radius: 26px;
      padding: 38px 42px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 35px rgba(37, 211, 102, 0.08);
      margin-top: 24px;
    }

    .wa-card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      padding-bottom: 24px;
      margin-bottom: 28px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      flex-wrap: wrap;
    }

    .wa-badge-box {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .wa-title {
      font-size: clamp(1.25rem, 1.1rem + .8vw, 1.7rem);
      font-weight: 800;
      color: #ffffff;
      margin: 0;
      letter-spacing: -0.02em;
    }

    .wa-sub {
      font-size: 13px;
      color: var(--muted-d);
      margin: 4px 0 0 0;
    }

    .wa-live-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(37, 211, 102, 0.12);
      border: 1px solid rgba(37, 211, 102, 0.4);
      color: #25D366;
      padding: 6px 14px;
      border-radius: 100px;
      font-size: 12.5px;
      font-weight: 700;
    }

    .wa-steps-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 32px;
    }

    .wa-step {
      background: #17181c;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 22px 20px;
      position: relative;
    }

    .wa-step-num {
      font-family: var(--font-mono, monospace);
      font-size: 12px;
      font-weight: 800;
      color: #25D366;
      background: rgba(37, 211, 102, 0.15);
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-block;
      margin-bottom: 12px;
    }

    .wa-step h4 {
      font-size: 15px;
      font-weight: 700;
      color: #ffffff;
      margin: 0 0 6px 0;
    }

    .wa-step p {
      font-size: 12.5px;
      color: var(--muted-d);
      line-height: 1.5;
      margin: 0;
    }

    .wa-cta-box {
      background: rgba(37, 211, 102, 0.08);
      border: 1.5px solid rgba(37, 211, 102, 0.35);
      border-radius: 18px;
      padding: 24px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
    }

    .wa-cta-info strong {
      display: block;
      color: #ffffff;
      font-size: 13.5px;
      margin-bottom: 4px;
    }

    .wa-link-text {
      font-family: var(--font-mono, monospace);
      font-size: 13px;
      color: #25D366;
      word-break: break-all;
    }

    .btn-whatsapp {
      background: #25D366;
      color: #0b0b0b !important;
      font-weight: 800;
      font-size: 14.5px;
      padding: 13px 26px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      transition: filter .2s ease, transform .2s ease, box-shadow .2s ease;
      box-shadow: 0 8px 24px rgba(37, 211, 102, 0.35);
      white-space: nowrap;
    }

    .btn-whatsapp:hover {
      filter: brightness(1.12);
      transform: translateY(-2px);
      box-shadow: 0 12px 32px rgba(37, 211, 102, 0.5);
    }

    /* Floating WhatsApp Pill */
    .fab-wa {
      position: fixed;
      bottom: 26px;
      left: 26px;
      z-index: 999;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: #25D366;
      color: #0b0b0b !important;
      padding: 12px 20px;
      border-radius: 100px;
      font-weight: 800;
      font-size: 13.5px;
      text-decoration: none;
      box-shadow: 0 10px 30px rgba(37, 211, 102, 0.45);
      transition: transform .2s ease, box-shadow .2s ease, filter .2s ease;
    }

    .fab-wa:hover {
      filter: brightness(1.12);
      transform: translateY(-3px) scale(1.02);
      box-shadow: 0 14px 40px rgba(37, 211, 102, 0.6);
    }

    @media (max-width: 900px) {
      .wa-steps-grid { grid-template-columns: 1fr; }
      .wa-card { padding: 26px 22px; }
      .wa-cta-box { flex-direction: column; align-items: stretch; text-align: center; }
      .btn-whatsapp { width: 100%; justify-content: center; }
    }

    @media (max-width: 600px) {
      .fab-wa-txt { display: none; }
      .fab-wa { padding: 14px; border-radius: 50%; left: 16px; bottom: 16px; }
    }
"""

# 3. Contact Section HTML
contact_section_html = """  <!-- ============================================================
       CONTACT US & OFFICIAL WHATSAPP BUYER GROUP
       ============================================================ -->
  <section class="section contact-sec" id="contact" aria-labelledby="contact-title">
    <div class="wrap">
      <div class="sec-head">
        <div>
          <p class="sticker reveal" style="border-color: rgba(37, 211, 102, 0.4); background: rgba(37, 211, 102, 0.12); color: #25D366;">
            <span>Official Sales &amp; VIP Group</span>
          </p>
          <h2 class="reveal" id="contact-title">
            <span>Contact &amp; Buy</span>
            <mark style="color: #25D366; background: rgba(37, 211, 102, 0.1);">Via WhatsApp.</mark>
          </h2>
        </div>
        <p class="sec-note reveal">
          Join our official buyer community on WhatsApp. Message any group admin directly to select your plan, pay securely, and receive your instant license activation key.
        </p>
      </div>

      <!-- Main WhatsApp VIP Hero Card -->
      <div class="wa-card reveal">
        <div class="wa-card-top">
          <div class="wa-badge-box">
            <svg class="ic" style="width:36px; height:36px; color: #25D366;"><use href="#i-whatsapp"></use></svg>
            <div>
              <h3 class="wa-title">Downloader Pro Official Customer Group</h3>
              <p class="wa-sub">Direct Admin Communication &bull; Instant License Issuance &bull; 24/7 Priority Support</p>
            </div>
          </div>
          <span class="wa-live-pill">
            <span class="ov-dot" style="background:#25D366; box-shadow:0 0 10px #25D366;"></span>
            <span>Admins Online Now</span>
          </span>
        </div>

        <div class="wa-card-body">
          <div class="wa-steps-grid">
            <div class="wa-step">
              <span class="wa-step-num">STEP 01</span>
              <h4>Join WhatsApp Group</h4>
              <p>Click the invite link below to join our verified community of Downloader Pro creators and buyers.</p>
            </div>
            <div class="wa-step">
              <span class="wa-step-num">STEP 02</span>
              <h4>Message Any Admin</h4>
              <p>Contact an admin in the group stating your desired plan: Monthly ($1.99), Annual ($14.99), or Lifetime ($24.99).</p>
            </div>
            <div class="wa-step">
              <span class="wa-step-num">STEP 03</span>
              <h4>Instant Activation Key</h4>
              <p>Pay securely via your preferred method. Admin will generate and deliver your cryptographically signed key immediately.</p>
            </div>
          </div>

          <div class="wa-cta-box">
            <div class="wa-cta-info">
              <strong>Official WhatsApp Group Link:</strong>
              <span class="wa-link-text">https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG</span>
            </div>
            <a href="https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" id="btnJoinWhatsAppGroup">
              <svg class="ic" style="width:20px; height:20px;"><use href="#i-whatsapp"></use></svg>
              <span>Join WhatsApp Group to Buy a Plan</span>
              <svg class="ic"><use href="#i-arrow-ne"></use></svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>

"""

# 4. Floating WhatsApp Pill HTML
floating_wa_html = """  <!-- Floating WhatsApp Buyer Group Button -->
  <a href="https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG" target="_blank" rel="noopener noreferrer" class="fab-wa" id="fabWhatsApp" title="Join WhatsApp Group & Buy Plan" aria-label="Join WhatsApp Group">
    <svg class="ic" style="width:24px; height:24px;" aria-hidden="true"><use href="#i-whatsapp"></use></svg>
    <span class="fab-wa-txt">Buy via WhatsApp</span>
  </a>
"""

# 5. Modal WhatsApp Box
modal_wa_html = """        <!-- Direct WhatsApp Admin Purchase Box -->
        <div class="modal-wa-box" style="background: rgba(37, 211, 102, 0.08); border: 1.5px solid rgba(37, 211, 102, 0.35); border-radius: 14px; padding: 16px; margin-bottom: 20px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
            <svg class="ic" style="width:20px; height:20px; color:#25D366;"><use href="#i-whatsapp"></use></svg>
            <strong style="color:#ffffff; font-size:13.5px;">Direct Purchase via WhatsApp</strong>
          </div>
          <p style="font-size:12.5px; color:var(--muted-d); margin:0 0 12px 0; line-height:1.45;">
            Buyers must join our official WhatsApp group and contact the admins to purchase a license plan:
          </p>
          <a href="https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" style="width:100%; justify-content:center; padding:10px 18px; font-size:13px;">
            <svg class="ic" style="width:17px; height:17px;"><use href="#i-whatsapp"></use></svg>
            <span>Join WhatsApp Group &amp; Contact Admins &rarr;</span>
          </a>
        </div>
"""

def update_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add SVG symbol
    if 'id="i-whatsapp"' not in content:
        content = content.replace("  </svg>", wa_symbol, 1)
        print(f"[OK] Added i-whatsapp symbol to {filepath}")

    # 2. Add CSS
    if "/* CONTACT & WHATSAPP BUYER GROUP SECTION */" not in content and ".contact-sec {" not in content:
        p_css = content.find("</style>")
        if p_css != -1:
            content = content[:p_css] + wa_css + "\n</style>" + content[p_css + 8:]
            print(f"[OK] Added WhatsApp CSS to {filepath}")

    # 3. Update Nav Links
    if '<a href="#contact">Contact</a>' not in content:
        content = content.replace('<a href="#pricing">Pricing</a>', '<a href="#pricing">Pricing</a>\n        <a href="#contact">Contact &amp; VIP Group</a>')
        print(f"[OK] Added Contact to desktop nav in {filepath}")

    if '<a href="#contact">Contact &amp; Buy Plan</a>' not in content:
        content = content.replace('<a href="#pricing">License Passes</a>', '<a href="#pricing">License Passes</a>\n    <a href="#contact">Contact &amp; Buy Plan</a>')
        print(f"[OK] Added Contact to mobile menu in {filepath}")

    # 4. Add Contact Section before Closing CTA
    closing_marker = "  <!-- ============================================================\n       CLOSING CTA"
    if 'id="contact"' not in content:
        if closing_marker in content:
            content = content.replace(closing_marker, contact_section_html + closing_marker, 1)
            print(f"[OK] Added Contact Section before Closing CTA in {filepath}")
        else:
            print(f"[WARN] closing_marker not found in {filepath}")

    # 5. Add Modal WhatsApp Box
    modal_marker = '<div id="checkoutFormStep">'
    if 'Direct Purchase via WhatsApp' not in content:
        if modal_marker in content:
            # Place after modal subtitle
            sub_marker = 'Instant activation key delivered on screen and saved locally.\n        </p>'
            if sub_marker in content:
                content = content.replace(sub_marker, sub_marker + "\n\n" + modal_wa_html, 1)
                print(f"[OK] Added WhatsApp box to Checkout Modal in {filepath}")

    # 6. Add Floating WhatsApp Pill
    fab_marker = '<a href="https://drive.google.com/file/'
    if 'id="fabWhatsApp"' not in content:
        p_fab = content.find('id="fabBtn"')
        if p_fab != -1:
            # find end of fabBtn </a>
            p_end_fab = content.find("</a>", p_fab)
            if p_end_fab != -1:
                content = content[:p_end_fab + 4] + "\n\n" + floating_wa_html + content[p_end_fab + 4:]
                print(f"[OK] Added Floating WhatsApp button in {filepath}")

    # 7. Add WhatsApp to Footer
    footer_explore_marker = '<a href="#pricing">Upgrade to Pro</a>'
    if 'WhatsApp Buyer Group' not in content:
        if footer_explore_marker in content:
            content = content.replace(footer_explore_marker, footer_explore_marker + '\n        <a href="https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG" target="_blank" rel="noopener noreferrer" style="color:#25D366; font-weight:700;">💬 WhatsApp VIP Buyer Group</a>\n        <a href="#contact">Contact &amp; Admin Support</a>', 1)
            print(f"[OK] Added WhatsApp links to footer in {filepath}")

    with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)

for f in html_files + py_files:
    update_file(f)

print("WhatsApp Contact feature migration complete!")
