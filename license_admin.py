"""
Seller License Admin Tool for Media Downloader Pro
Provides an interactive GUI and CLI for generating subscription keys,
viewing activations, and managing customer licenses.
"""

import os
import sys
import argparse
import subprocess
import threading
from datetime import datetime
from typing import Optional

# Ensure local imports work
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from backend.database import (
    init_db,
    create_license,
    list_all_licenses,
    revoke_license,
    unrevoke_license,
    delete_license,
    get_connection
)
from backend.keygen import (
    generate_license_key,
    calculate_expiry,
    PLAN_CODES
)

# Initialize database
init_db()


def cli_generate(plan: str, customer: str, email: str = "", max_devs: int = 1):
    key = generate_license_key(plan)
    exp = calculate_expiry(plan)
    lic = create_license(
        license_key=key,
        plan=plan,
        customer_name=customer,
        customer_email=email,
        expires_at=exp,
        max_activations=max_devs
    )
    exp_str = exp.strftime("%Y-%m-%d") if exp else "Lifetime (Never)"
    print("\n" + "=" * 55)
    print("      NEW LICENSE KEY GENERATED")
    print("=" * 55)
    print(f"Key:          {key}")
    print(f"Plan:         {plan.replace('_', ' ').title()}")
    print(f"Customer:     {customer or 'N/A'}")
    print(f"Expires:      {exp_str}")
    print(f"Max Devices:  {max_devs} PC")
    print("=" * 55)
    return key


def cli_list():
    licenses = list_all_licenses()
    print("\n" + "=" * 80)
    print(f"{'LICENSE KEY':<26} {'CUSTOMER':<18} {'PLAN':<14} {'DEVICES':<8} {'EXPIRES':<12}")
    print("=" * 80)
    for l in licenses:
        exp = l.get('expires_at')
        exp_s = exp.split('T')[0] if exp else 'Lifetime'
        status = "REVOKED" if l.get('is_revoked') else f"{l.get('activations_count', 0)}/{l.get('max_activations', 1)}"
        print(f"{l['license_key']:<26} {(l['customer_name'] or 'N/A')[:17]:<18} {l['plan']:<14} {status:<8} {exp_s:<12}")
    print("=" * 80 + "\n")


def cli_revoke(key: str):
    ok = revoke_license(key)
    if ok:
        print(f"\n[SUCCESS] License {key} has been terminated.")
        print("Customer Pro abilities have been revoked and disabled on all their machines.\n")
    else:
        print(f"\n[ERROR] License {key} not found.\n")


def cli_unrevoke(key: str):
    ok = unrevoke_license(key)
    if ok:
        print(f"\n[SUCCESS] License {key} has been restored and unrevoked.\n")
    else:
        print(f"\n[ERROR] License {key} not found.\n")


def cli_delete(key: str):
    ok = delete_license(key)
    if ok:
        print(f"\n[SUCCESS] License {key} has been permanently deleted from database.\n")
    else:
        print(f"\n[ERROR] License {key} not found.\n")


def launch_gui():
    """Launch Modern CustomTkinter Admin GUI for Seller."""
    import customtkinter as ctk
    import pyperclip

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Media Downloader Pro — Seller License Manager & Control Center")
    root.geometry("980x700")
    root.minsize(880, 560)

    # Header
    hdr = ctk.CTkFrame(root, corner_radius=0, fg_color="#18181F", height=65)
    hdr.pack(fill="x", side="top")
    hdr.pack_propagate(False)

    lbl_title = ctk.CTkLabel(
        hdr,
        text="👑 Media Downloader Pro — Seller License Manager",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#F9FAFB"
    )
    lbl_title.pack(side="left", padx=20, pady=15)

    badge = ctk.CTkLabel(
        hdr,
        text="ADMIN DASHBOARD",
        font=ctk.CTkFont(size=11, weight="bold"),
        fg_color="#E50914",
        text_color="#FFFFFF",
        corner_radius=6,
        padx=8,
        pady=3
    )
    badge.pack(side="right", padx=20)

    # Main Scrollable Body
    body = ctk.CTkScrollableFrame(root, fg_color="#0F0F12")
    body.pack(fill="both", expand=True, padx=20, pady=15)

    # 1. Generator Card
    gen_card = ctk.CTkFrame(body, fg_color="#1C1C24", corner_radius=10, border_width=1, border_color="#2D2D3A")
    gen_card.pack(fill="x", pady=(0, 15), padx=5)

    gen_header = ctk.CTkLabel(
        gen_card,
        text="⚡ Generate New Customer License Key",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color="#F9FAFB"
    )
    gen_header.pack(anchor="w", padx=20, pady=(15, 10))

    form_frame = ctk.CTkFrame(gen_card, fg_color="transparent")
    form_frame.pack(fill="x", padx=20, pady=(0, 15))

    # Grid columns
    form_frame.columnconfigure(0, weight=1)
    form_frame.columnconfigure(1, weight=1)
    form_frame.columnconfigure(2, weight=1)

    # Plan Choice
    ctk.CTkLabel(form_frame, text="Subscription Plan:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9CA3AF").grid(row=0, column=0, sticky="w", pady=(0, 4))
    plan_var = ctk.StringVar(value="pro_yearly")
    plan_menu = ctk.CTkOptionMenu(
        form_frame,
        variable=plan_var,
        values=["pro_monthly", "pro_yearly", "pro_lifetime"],
        fg_color="#272733",
        button_color="#3B82F6",
        button_hover_color="#2563EB"
    )
    plan_menu.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))

    # Customer Name
    ctk.CTkLabel(form_frame, text="Customer Name:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9CA3AF").grid(row=0, column=1, sticky="w", pady=(0, 4))
    name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g. John Doe", fg_color="#272733", border_color="#3A3A48")
    name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

    # Max Devices
    ctk.CTkLabel(form_frame, text="Max PC Activations:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#9CA3AF").grid(row=0, column=2, sticky="w", pady=(0, 4))
    dev_var = ctk.StringVar(value="1")
    dev_menu = ctk.CTkOptionMenu(
        form_frame,
        variable=dev_var,
        values=["1", "2", "3", "5"],
        fg_color="#272733",
        button_color="#3B82F6",
        button_hover_color="#2563EB"
    )
    dev_menu.grid(row=1, column=2, sticky="ew", pady=(0, 10))

    # Result Box
    res_frame = ctk.CTkFrame(gen_card, fg_color="#121217", corner_radius=8, border_width=1, border_color="#2A2A38")
    res_frame.pack(fill="x", padx=20, pady=(0, 15))

    lbl_key_disp = ctk.CTkLabel(
        res_frame,
        text="Click 'Generate Key' below to issue a new subscription",
        font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
        text_color="#60A5FA"
    )
    lbl_key_disp.pack(side="left", padx=15, pady=12)

    btn_copy = ctk.CTkButton(
        res_frame,
        text="📋 Copy Key",
        width=110,
        height=32,
        fg_color="#374151",
        hover_color="#4B5563",
        state="disabled"
    )
    btn_copy.pack(side="right", padx=15)

    def do_copy():
        key = lbl_key_disp.cget("text")
        if key and "MDP-" in key:
            pyperclip.copy(key)
            btn_copy.configure(text="✓ Copied!", fg_color="#10B981")
            root.after(2000, lambda: btn_copy.configure(text="📋 Copy Key", fg_color="#374151"))

    btn_copy.configure(command=do_copy)

    def on_generate():
        plan = plan_var.get()
        cust = name_entry.get().strip() or "Valued Customer"
        max_d = int(dev_var.get())
        new_key = cli_generate(plan, cust, max_devs=max_d)
        lbl_key_disp.configure(text=new_key, text_color="#34D399")
        btn_copy.configure(state="normal")
        name_entry.delete(0, "end")
        refresh_table()

    btn_gen = ctk.CTkButton(
        gen_card,
        text="✨ Generate & Issue License Key",
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color="#E50914",
        hover_color="#BF0811",
        height=40,
        command=on_generate
    )
    btn_gen.pack(fill="x", padx=20, pady=(0, 15))

    # 2. Existing Licenses Card
    list_card = ctk.CTkFrame(body, fg_color="#1C1C24", corner_radius=10, border_width=1, border_color="#2D2D3A")
    list_card.pack(fill="both", expand=True, padx=5, pady=(0, 15))

    list_header_frame = ctk.CTkFrame(list_card, fg_color="transparent")
    list_header_frame.pack(fill="x", padx=20, pady=(15, 6))

    ctk.CTkLabel(
        list_header_frame,
        text="📋 Issued Customer Licenses & Access Control",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color="#F9FAFB"
    ).pack(side="left")

    btn_refresh = ctk.CTkButton(
        list_header_frame,
        text="🔄 Refresh List",
        width=100,
        height=28,
        fg_color="#272733",
        hover_color="#3A3A48",
        command=lambda: refresh_table()
    )
    btn_refresh.pack(side="right")

    # Toast / Notification banner
    toast_lbl = ctk.CTkLabel(
        list_card,
        text="ℹ️ Click 'Terminate' to revoke a license and immediately disable customer Pro abilities.",
        font=ctk.CTkFont(size=11),
        text_color="#9CA3AF"
    )
    toast_lbl.pack(anchor="w", padx=20, pady=(0, 8))

    def show_toast(msg: str, is_error: bool = False):
        toast_lbl.configure(text=msg, text_color="#EF4444" if is_error else "#10B981")

    table_container = ctk.CTkFrame(list_card, fg_color="transparent")
    table_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def confirm_terminate(key_str: str, cust_name: str):
        modal = ctk.CTkToplevel(root)
        modal.title("Terminate License?")
        modal.geometry("480x270")
        modal.transient(root)
        modal.grab_set()

        root.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() - 480) // 2
        y = root.winfo_y() + (root.winfo_height() - 270) // 2
        modal.geometry(f"+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(modal, fg_color="#18181F", corner_radius=0)
        f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            f,
            text="🚫 Terminate Customer License?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#EF4444"
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            f,
            text=f"License Key: {key_str}\nCustomer: {cust_name}\n\nTerminating this license will immediately revoke it and disable Pro abilities on all customer PCs.\n\nAre you sure you want to proceed?",
            font=ctk.CTkFont(size=12),
            text_color="#D1D5DB",
            justify="left",
            wraplength=430
        ).pack(anchor="w", pady=(0, 16))

        b_row = ctk.CTkFrame(f, fg_color="transparent")
        b_row.pack(fill="x", side="bottom")

        def do_terminate():
            revoke_license(key_str)
            modal.destroy()
            show_toast(f"✔ License {key_str} has been terminated! Customer Pro abilities revoked.")
            refresh_table()

        ctk.CTkButton(
            b_row,
            text="Yes, Terminate License",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            height=36,
            command=do_terminate
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            b_row,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            fg_color="#374151",
            hover_color="#4B5563",
            width=80,
            height=36,
            command=modal.destroy
        ).pack(side="left")

    def confirm_delete(key_str: str, cust_name: str):
        modal = ctk.CTkToplevel(root)
        modal.title("Delete License Record?")
        modal.geometry("480x250")
        modal.transient(root)
        modal.grab_set()

        root.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() - 480) // 2
        y = root.winfo_y() + (root.winfo_height() - 250) // 2
        modal.geometry(f"+{max(0, x)}+{max(0, y)}")

        f = ctk.CTkFrame(modal, fg_color="#18181F", corner_radius=0)
        f.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            f,
            text="🗑️ Permanently Delete License?",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F87171"
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            f,
            text=f"License Key: {key_str}\nCustomer: {cust_name}\n\nPermanently remove this license record from the database? This cannot be undone.",
            font=ctk.CTkFont(size=12),
            text_color="#D1D5DB",
            justify="left",
            wraplength=430
        ).pack(anchor="w", pady=(0, 16))

        b_row = ctk.CTkFrame(f, fg_color="transparent")
        b_row.pack(fill="x", side="bottom")

        def do_delete():
            delete_license(key_str)
            modal.destroy()
            show_toast(f"✔ License {key_str} permanently deleted from database.")
            refresh_table()

        ctk.CTkButton(
            b_row,
            text="Yes, Permanently Delete",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            height=36,
            command=do_delete
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            b_row,
            text="Cancel",
            font=ctk.CTkFont(size=12),
            fg_color="#374151",
            hover_color="#4B5563",
            width=80,
            height=36,
            command=modal.destroy
        ).pack(side="left")

    def refresh_table():
        for widget in table_container.winfo_children():
            widget.destroy()

        licenses = list_all_licenses()
        if not licenses:
            ctk.CTkLabel(table_container, text="No licenses issued yet.", text_color="#9CA3AF").pack(pady=20)
            return

        # Table header
        hdr_row = ctk.CTkFrame(table_container, fg_color="#14141A", height=32, corner_radius=6)
        hdr_row.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(hdr_row, text="LICENSE KEY", width=195, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=10)
        ctk.CTkLabel(hdr_row, text="CUSTOMER", width=130, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=5)
        ctk.CTkLabel(hdr_row, text="PLAN", width=90, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=5)
        ctk.CTkLabel(hdr_row, text="DEVICES", width=65, anchor="center", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=5)
        ctk.CTkLabel(hdr_row, text="EXPIRES", width=95, anchor="center", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=5)
        ctk.CTkLabel(hdr_row, text="STATUS", width=95, anchor="center", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=5)
        ctk.CTkLabel(hdr_row, text="ACTIONS", width=220, anchor="center", font=ctk.CTkFont(size=11, weight="bold"), text_color="#9CA3AF").pack(side="left", padx=5)

        for lic in licenses:
            row = ctk.CTkFrame(table_container, fg_color="#20202A", height=40, corner_radius=6)
            row.pack(fill="x", pady=2)

            k_text = lic['license_key']
            cust_name = lic.get('customer_name') or 'N/A'
            is_rev = bool(lic.get('is_revoked'))

            key_color = "#9CA3AF" if is_rev else "#60A5FA"
            ctk.CTkLabel(row, text=k_text, width=195, anchor="w", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color=key_color).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=cust_name[:17], width=130, anchor="w", font=ctk.CTkFont(size=12), text_color="#F9FAFB").pack(side="left", padx=5)

            p_title = lic.get('plan', '').replace('pro_', '').title()
            ctk.CTkLabel(row, text=p_title, width=90, anchor="w", font=ctk.CTkFont(size=12), text_color="#F472B6").pack(side="left", padx=5)

            dev_str = f"{lic.get('activations_count', 0)}/{lic.get('max_activations', 1)}"
            ctk.CTkLabel(row, text=dev_str, width=65, anchor="center", font=ctk.CTkFont(size=12), text_color="#9CA3AF" if is_rev else "#34D399").pack(side="left", padx=5)

            exp = lic.get('expires_at')
            exp_str = exp.split('T')[0] if exp else 'Lifetime'
            ctk.CTkLabel(row, text=exp_str, width=95, anchor="center", font=ctk.CTkFont(size=11), text_color="#9CA3AF").pack(side="left", padx=5)

            # Status pill
            if is_rev:
                status_lbl = ctk.CTkLabel(
                    row,
                    text="TERMINATED",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#EF4444",
                    fg_color="#450A0A",
                    corner_radius=4,
                    width=95,
                    height=22
                )
            else:
                status_lbl = ctk.CTkLabel(
                    row,
                    text="ACTIVE",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#10B981",
                    fg_color="#064E3B",
                    corner_radius=4,
                    width=95,
                    height=22
                )
            status_lbl.pack(side="left", padx=5)

            # Action buttons
            actions_box = ctk.CTkFrame(row, fg_color="transparent")
            actions_box.pack(side="left", padx=5)

            # 1. Copy button
            ctk.CTkButton(
                actions_box,
                text="Copy",
                width=50,
                height=26,
                fg_color="#374151",
                hover_color="#4B5563",
                font=ctk.CTkFont(size=11),
                command=lambda k=k_text: [pyperclip.copy(k), show_toast(f"✔ Copied key: {k}")]
            ).pack(side="left", padx=2)

            # 2. Terminate or Restore button
            if not is_rev:
                ctk.CTkButton(
                    actions_box,
                    text="🚫 Terminate",
                    width=85,
                    height=26,
                    fg_color="#DC2626",
                    hover_color="#B91C1C",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda k=k_text, c=cust_name: confirm_terminate(k, c)
                ).pack(side="left", padx=2)
            else:
                ctk.CTkButton(
                    actions_box,
                    text="↺ Restore",
                    width=75,
                    height=26,
                    fg_color="#059669",
                    hover_color="#047857",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda k=k_text: [unrevoke_license(k), refresh_table(), show_toast(f"✔ Restored license: {k}")]
                ).pack(side="left", padx=2)

            # 3. Delete button
            ctk.CTkButton(
                actions_box,
                text="🗑️ Delete",
                width=65,
                height=26,
                fg_color="#1F2937",
                hover_color="#7F1D1D",
                font=ctk.CTkFont(size=11),
                command=lambda k=k_text, c=cust_name: confirm_delete(k, c)
            ).pack(side="left", padx=2)

    refresh_table()
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Media Downloader Pro — Seller License Admin")
    parser.add_argument("--generate", action="store_true", help="Generate a new license key")
    parser.add_argument("--plan", choices=["pro_monthly", "pro_yearly", "pro_lifetime"], default="pro_yearly")
    parser.add_argument("--customer", default="Valued Customer", help="Customer Name")
    parser.add_argument("--email", default="", help="Customer Email")
    parser.add_argument("--devices", type=int, default=1, help="Max PC Activations")
    parser.add_argument("--list", action="store_true", help="List all issued license keys")
    parser.add_argument("--revoke", metavar="KEY", help="Terminate a license key immediately and disable Pro abilities")
    parser.add_argument("--terminate", metavar="KEY", help="Alias for --revoke")
    parser.add_argument("--unrevoke", metavar="KEY", help="Restore a terminated license key")
    parser.add_argument("--delete", metavar="KEY", help="Permanently delete a license key from database")
    parser.add_argument("--gui", action="store_true", help="Launch interactive GUI")

    args = parser.parse_args()

    if args.generate:
        cli_generate(args.plan, args.customer, args.email, args.devices)
    elif args.list:
        cli_list()
    elif args.revoke or args.terminate:
        cli_revoke(args.revoke or args.terminate)
    elif args.unrevoke:
        cli_unrevoke(args.unrevoke)
    elif args.delete:
        cli_delete(args.delete)
    else:
        # Default to GUI when double clicked or run without flags
        launch_gui()
