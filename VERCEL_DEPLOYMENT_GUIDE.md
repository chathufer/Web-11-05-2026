# 🚀 Vercel Deployment & Domain Guide for prodownloader.site

This project is now 100% turnkey ready for deployment to **Vercel** with your custom domain **prodownloader.site**.

---

## 📁 What Was Configured for Vercel

1. **`vercel.json`**: Configured for Vercel's `@vercel/python` serverless runtime.
2. **`api/index.py`**: Serverless function entrypoint exposing the Flask app.
3. **`backend/database.py`**: Added automatic `/tmp/licenses.db` writable storage support for Vercel's ephemeral serverless filesystem.
4. **`licensing.py`**: Configured `https://prodownloader.site` as the primary production licensing URL.
5. **`Setup/MediaDownloaderPro_Setup.exe`**: Freshly compiled with `prodownloader.site` embedded.

---

## 🌐 Step 1: Deploy to Vercel (2 Minutes)

### Option A: Via GitHub (Recommended)
1. Push this project folder to a repository on **[GitHub](https://github.com/)** (Private or Public).
2. Go to **[vercel.com](https://vercel.com/)** and log in (Free Hobby Plan).
3. Click **"Add New..." ➜ "Project"**.
4. Select your GitHub repository and click **"Import"**.
5. Under **Environment Variables**, add:
   * `ADMIN_API_KEY`: `MDP_ADMIN_SECRET_KEY_2026` (your seller admin password)
   * `INSTALLER_DOWNLOAD_URL`: *(See Step 3 below for hosting the 90MB file)*
6. Click **"Deploy"**!

### Option B: Via Vercel CLI (Direct Terminal)
In your workspace terminal, simply run:
```powershell
npx vercel
```
Follow the on-screen prompts to link and deploy in seconds!

---

## 🔗 Step 2: Connect Your Domain (`prodownloader.site`)

1. In your **Vercel Project Dashboard**, navigate to **Settings ➜ Domains**.
2. Type `prodownloader.site` and click **"Add"**.
3. Choose the recommended option (redirect `www.prodownloader.site` to `prodownloader.site`).
4. Vercel will show you the exact DNS records to add at your domain registrar (Namecheap, GoDaddy, Hostinger, Cloudflare, etc.):
   * **A Record**:
     * Host/Name: `@`
     * Value/IP: `76.76.21.21`
   * **CNAME Record**:
     * Host/Name: `www`
     * Value: `cname.vercel-dns.com`
5. Vercel will automatically verify the records and issue a **free automated SSL Certificate (HTTPS)** within 1-5 minutes!

---

## 📦 Step 3: Hosting the 90 MB Installer File

> **Note on Vercel**: Vercel Serverless Functions have a 4.5 MB payload response limit. Since `MediaDownloaderPro_Setup.exe` is ~90 MB, it should be hosted on a free global CDN.

### Recommended Free Options:
1. **GitHub Releases (Free & Unlimited Global Speed)**:
   * In your GitHub repo, click **Releases ➜ Draft a new release**.
   * Tag it `v2.2.0`, attach `Setup/MediaDownloaderPro_Setup.exe`, and click **Publish Release**.
   * Copy the direct download link of the uploaded `.exe`.
2. **Google Drive / Dropbox / Cloudflare R2**:
   * Upload `MediaDownloaderPro_Setup.exe` and generate a direct download link.
3. **Set the Environment Variable in Vercel**:
   * In Vercel ➜ Project Settings ➜ Environment Variables:
     * Key: `INSTALLER_DOWNLOAD_URL`
     * Value: `https://github.com/your-username/your-repo/releases/download/v2.2.0/DownloaderPro_Setup.exe`
   * When visitors click **"Download"** on `prodownloader.site`, the server instantly redirects them to download the file at maximum CDN speed!

---

## 👑 What Runs on `prodownloader.site`

Once deployed, your domain will serve:
* **`https://prodownloader.site/`**: Dark-themed commercial storefront for Downloader Pro with pricing, features, and instant checkout.
* **`https://prodownloader.site/download`**: Fast download link for the installer.
* **`https://prodownloader.site/admin`**: Your password-protected seller dashboard for managing, generating, and terminating customer keys.
* **`https://prodownloader.site/api/v1/license/activate`**: Online license activation endpoint used by the desktop app on customer PCs worldwide!
