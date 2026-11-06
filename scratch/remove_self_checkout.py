import os

base_dir = r"c:\Users\Chathufer\Downloads\Youtube video dowonloader"

html_files = [
    os.path.join(base_dir, "index.html"),
    os.path.join(base_dir, "public", "index.html"),
    os.path.join(base_dir, "deploy_vercel", "index.html"),
    os.path.join(base_dir, "deploy_vercel", "public", "index.html"),
]

py_web_files = [
    os.path.join(base_dir, "backend", "website_html.py"),
    os.path.join(base_dir, "deploy_vercel", "backend", "website_html.py"),
]

server_files = [
    os.path.join(base_dir, "backend", "server.py"),
    os.path.join(base_dir, "deploy_vercel", "backend", "server.py"),
]

# 1. New Modal HTML (strictly WhatsApp buy flow, NO key generation, NO fake keys)
new_modal_html = """  <!-- ============================================================
       CHECKOUT MODAL DIALOG (WHATSAPP ADMIN PURCHASE ONLY)
       ============================================================ -->
  <dialog id="checkoutModal">
    <div class="modal-box">
      <button class="modal-close" id="modalCloseBtn" aria-label="Close dialog">
        <svg class="ic"><use href="#i-close"></use></svg>
      </button>

      <div id="checkoutFormStep">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
          <svg class="ic" style="width: 28px; height: 28px; color: #25D366;"><use href="#i-whatsapp"></use></svg>
          <h3 style="font-size: 22px; margin: 0; color: #ffffff;">Purchase Downloader Pro</h3>
        </div>
        <p style="font-size: 13.5px; color: var(--muted-d); margin-bottom: 20px; line-height: 1.5;">
          All official license keys are generated and issued directly by admins. Join our official WhatsApp VIP group to complete your purchase and receive your license key.
        </p>

        <div class="form-group" style="margin-bottom: 18px;">
          <label for="checkoutPlan" style="display: block; font-size: 13px; font-weight: 700; color: var(--paper); margin-bottom: 8px;">Selected Plan to Purchase</label>
          <select id="checkoutPlan" class="form-input" style="cursor:pointer; width: 100%; padding: 12px 14px; background: var(--ink-2); border: 1.5px solid var(--ink-line); border-radius: 10px; color: var(--paper); font-size: 14px;">
            <option value="pro_lifetime">Lifetime Master Pass ($24.99 one-time)</option>
            <option value="pro_yearly">Annual Pro Pass ($14.99 / year)</option>
            <option value="pro_monthly">Monthly Pro Pass ($1.99 / month)</option>
          </select>
        </div>

        <div style="background: rgba(37, 211, 102, 0.08); border: 1.5px solid rgba(37, 211, 102, 0.35); border-radius: 14px; padding: 16px 18px; margin-bottom: 20px;">
          <strong style="display: block; color: #ffffff; font-size: 13px; margin-bottom: 8px;">How to Buy from Admin:</strong>
          <ol style="margin: 0; padding-left: 20px; color: var(--muted-d); font-size: 12.5px; line-height: 1.6;">
            <li>Click the button below to join our official WhatsApp group.</li>
            <li>Message any group admin with your selected plan name.</li>
            <li>Complete payment, and the admin will generate and deliver your official license key immediately.</li>
          </ol>
        </div>

        <a href="https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp" id="btnJoinWhatsAppModal" style="width: 100%; justify-content: center; padding: 14px 20px; font-size: 15px; box-sizing: border-box;">
          <svg class="ic" style="width: 20px; height: 20px;"><use href="#i-whatsapp"></use></svg>
          <span>Join WhatsApp Group to Buy Plan</span>
          <svg class="ic"><use href="#i-arrow-ne"></use></svg>
        </a>

        <p style="text-align: center; font-size: 11.5px; color: var(--muted-d); margin-top: 14px; margin-bottom: 0;">
          Direct Invite Link: <span style="color: #25D366; font-family: var(--font-mono, monospace);">chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG</span>
        </p>
      </div>
    </div>
  </dialog>"""

# 2. New JS for Checkout modal (only open/close and set plan, NO key generation)
new_js_checkout = """      // ---------- Checkout Modal (Direct to WhatsApp Group) ----------
      const checkoutModal = $('#checkoutModal');
      const modalCloseBtn = $('#modalCloseBtn');
      const checkoutPlanSelect = $('#checkoutPlan');
      const checkoutTriggers = $$('.trigger-checkout');

      checkoutTriggers.forEach(btn => {
        btn.addEventListener('click', () => {
          const plan = btn.dataset.plan || 'pro_lifetime';
          if (checkoutPlanSelect) checkoutPlanSelect.value = plan;
          if (checkoutModal && typeof checkoutModal.showModal === 'function') {
            checkoutModal.showModal();
          }
        });
      });

      if (modalCloseBtn && checkoutModal) {
        modalCloseBtn.addEventListener('click', () => checkoutModal.close());
        checkoutModal.addEventListener('click', (e) => { if (e.target === checkoutModal) checkoutModal.close(); });
      }
    })();"""

# Old modal markers
modal_start_tag = "  <!-- ============================================================\n       CHECKOUT MODAL DIALOG\n       ============================================================ -->\n  <dialog id=\"checkoutModal\">"
modal_end_tag = "  </dialog>"

# Old JS checkout markers
old_js_checkout_start = "      // ---------- Checkout Modal & Live License Generation ----------"
old_js_checkout_end = "    })();"

def update_web_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Replace modal HTML
    p_m1 = text.find(modal_start_tag)
    p_m2 = text.find(modal_end_tag, p_m1)
    if p_m1 != -1 and p_m2 != -1:
        text = text[:p_m1] + new_modal_html + text[p_m2 + len(modal_end_tag):]
        print(f"[OK] Replaced Checkout Modal in {filepath}")
    else:
        print(f"[WARN] Modal tags not found in {filepath}")

    # Replace JS checkout logic
    p_j1 = text.find(old_js_checkout_start)
    p_j2 = text.find(old_js_checkout_end, p_j1)
    if p_j1 != -1 and p_j2 != -1:
        text = text[:p_j1] + new_js_checkout + text[p_j2 + len(old_js_checkout_end):]
        print(f"[OK] Removed key generation JS in {filepath}")
    else:
        print(f"[WARN] JS checkout markers not found in {filepath}")

    with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(text)

for f in html_files + py_web_files:
    update_web_file(f)

# 3. Disable /api/v1/checkout in server.py
new_server_checkout = """@app.route("/api/v1/checkout", methods=["POST", "GET"])
def api_checkout():
    \"\"\"Disabled public key generation. Customers must contact admins on WhatsApp.\"\"\"
    return jsonify({
        "status": "contact_admin",
        "message": "Public key generation is disabled. Please contact admins in our official WhatsApp group to purchase a plan.",
        "whatsapp_url": "https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG"
    }), 403"""

def update_server_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    p1 = text.find('@app.route("/api/v1/checkout", methods=["POST"])')
    p2 = text.find('return jsonify({', p1)
    p3 = text.find('\n\n\n@app.route("/api/v1/latest"', p2)
    if p3 == -1:
        p3 = text.find('\n@app.route("/api/v1/latest"', p2)

    if p1 != -1 and p3 != -1:
        text = text[:p1] + new_server_checkout + text[p3:]
        with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(text)
        print(f"[OK] Disabled public key generation in {filepath}")
    else:
        print(f"[WARN] Could not find checkout route in {filepath}")

for f in server_files:
    update_server_file(f)

print("Self-checkout removal complete!")
