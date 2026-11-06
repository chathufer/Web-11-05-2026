files = ['backend/server.py', 'deploy_vercel/backend/server.py']

new_route = '''@app.route("/api/v1/checkout", methods=["POST", "GET"])
def api_checkout():
    """Disabled public key generation. Customers must contact admins in WhatsApp group to buy."""
    return jsonify({
        "status": "contact_admin",
        "message": "Public license key generation is disabled. Please contact admins in our official WhatsApp group to purchase a plan.",
        "whatsapp_url": "https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG"
    }), 403


'''

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    p1 = c.find('@app.route("/api/v1/checkout"')
    p2 = c.find('@app.route("/api/v1/health"', p1)
    
    if p1 != -1 and p2 != -1:
        c = c[:p1] + new_route + c[p2:]
        with open(f, 'w', encoding='utf-8', newline='\r\n') as fp:
            fp.write(c)
        print(f"[OK] Disabled api_checkout in {f}")
    else:
        print(f"[FAIL] Could not find markers in {f}")

print("Done!")
