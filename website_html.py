"""
Luxury Edition HTML & CSS Template for Downloader Pro (prodownloader.site).
Features deep obsidian dark aesthetic, liquid gold metallic accents, realistic photography,
scroll-triggered animations, interactive live preview switcher, and instant checkout.
"""

WEBSITE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloader Pro — Luxury High-Performance Media Downloader</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #05070B;
            --bg-surface: #090E17;
            --bg-card: rgba(14, 21, 37, 0.65);
            --bg-card-hover: rgba(20, 31, 54, 0.85);
            --border: rgba(255, 255, 255, 0.08);
            --border-gold: rgba(212, 175, 55, 0.35);
            --border-hover: rgba(212, 175, 55, 0.7);
            
            /* Luxury Metallic Gold Palette */
            --gold-100: #FFF6D6;
            --gold-200: #FFE5A3;
            --gold-300: #F3CA68;
            --gold-400: #D4AF37;
            --gold-500: #B38B1C;
            --gold-glow: rgba(212, 175, 55, 0.28);
            --gold-gradient: linear-gradient(135deg, #FFF1C5 0%, #D4AF37 45%, #996515 85%, #F5C542 100%);
            
            --cyan-glow: rgba(56, 189, 248, 0.2);
            --emerald: #10B981;
            --text-bright: #F8FAFC;
            --text-dim: #94A3B8;
            --text-muted: #64748B;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            scroll-behavior: smooth;
        }

        body {
            background-color: var(--bg-deep);
            color: var(--text-bright);
            line-height: 1.6;
            overflow-x: hidden;
            position: relative;
        }

        /* ---------------- LUXURY AMBIENT BACKGROUND GLOW ---------------- */
        .ambient-orb {
            position: fixed;
            border-radius: 50%;
            filter: blur(120px);
            pointer-events: none;
            z-index: 0;
            opacity: 0.6;
            animation: orbFloat 22s ease-in-out infinite alternate;
        }

        .ambient-orb.gold {
            width: 550px;
            height: 550px;
            background: radial-gradient(circle, rgba(212, 175, 55, 0.15) 0%, transparent 70%);
            top: -120px;
            left: 20%;
        }

        .ambient-orb.sapphire {
            width: 650px;
            height: 650px;
            background: radial-gradient(circle, rgba(37, 99, 235, 0.12) 0%, transparent 70%);
            top: 35%;
            right: -100px;
            animation-duration: 28s;
        }

        .ambient-orb.emerald {
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%);
            bottom: 10%;
            left: -80px;
        }

        @keyframes orbFloat {
            0% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(40px, 60px) scale(1.1); }
            100% { transform: translate(-30px, 30px) scale(0.95); }
        }

        /* Subtle luxury noise overlay */
        .noise-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 32px 32px;
            pointer-events: none;
            z-index: 1;
            opacity: 0.7;
        }

        .content-layer {
            position: relative;
            z-index: 2;
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        /* ---------------- SCROLL REVEAL ANIMATIONS ---------------- */
        .reveal {
            opacity: 0;
            transform: translateY(40px);
            filter: blur(6px);
            transition: opacity 0.85s cubic-bezier(0.16, 1, 0.3, 1), transform 0.85s cubic-bezier(0.16, 1, 0.3, 1), filter 0.85s cubic-bezier(0.16, 1, 0.3, 1);
            will-change: opacity, transform, filter;
        }

        .reveal.active {
            opacity: 1;
            transform: translateY(0);
            filter: blur(0);
        }

        .delay-1 { transition-delay: 0.12s; }
        .delay-2 { transition-delay: 0.24s; }
        .delay-3 { transition-delay: 0.36s; }
        .delay-4 { transition-delay: 0.48s; }

        /* ---------------- NAVBAR ---------------- */
        .navbar {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(5, 7, 11, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border);
            padding: 18px 32px;
            transition: all 0.3s;
        }

        .nav-container {
            max-width: 1240px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 21px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .logo-crown {
            font-size: 22px;
            filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.6));
        }

        .logo-text {
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Cinzel', serif;
            letter-spacing: 1px;
            font-weight: 700;
        }

        .badge-edition {
            background: rgba(212, 175, 55, 0.12);
            color: var(--gold-300);
            border: 1px solid var(--border-gold);
            font-size: 10px;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 4px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 32px;
        }

        .nav-link {
            color: var(--text-dim);
            font-size: 14px;
            font-weight: 600;
            transition: color 0.25s;
            position: relative;
        }

        .nav-link:hover {
            color: var(--gold-200);
        }

        .nav-link::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0%;
            height: 2px;
            background: var(--gold-gradient);
            transition: width 0.25s ease;
        }

        .nav-link:hover::after {
            width: 100%;
        }

        .nav-btn {
            background: var(--gold-gradient);
            color: #05070B;
            font-weight: 800;
            font-size: 13px;
            padding: 10px 22px;
            border-radius: 8px;
            box-shadow: 0 4px 18px var(--gold-glow);
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .nav-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 60%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            transform: skewX(-25deg);
            animation: shimmerSweep 3.5s infinite;
        }

        .nav-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(212, 175, 55, 0.5);
        }

        @keyframes shimmerSweep {
            0% { left: -100%; }
            20% { left: 160%; }
            100% { left: 160%; }
        }

        /* ---------------- HERO SECTION ---------------- */
        .hero {
            max-width: 1240px;
            margin: 0 auto;
            padding: 100px 24px 70px;
            text-align: center;
        }

        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(14, 21, 37, 0.7);
            border: 1px solid var(--border-gold);
            padding: 8px 18px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--gold-200);
            margin-bottom: 28px;
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.15);
        }

        .hero-pill .star-icon {
            color: var(--gold-300);
            font-size: 13px;
        }

        .hero-title {
            font-family: 'Cinzel', serif;
            font-size: 64px;
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -0.5px;
            margin-bottom: 24px;
        }

        .hero-title .gold-accent {
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }

        .hero-subtitle {
            font-size: 19px;
            color: var(--text-dim);
            max-width: 760px;
            margin: 0 auto 40px;
            line-height: 1.7;
            font-weight: 400;
        }

        .hero-actions {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-bottom: 48px;
        }

        .btn-luxury-gold {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: var(--gold-gradient);
            color: #05070B;
            font-size: 15px;
            font-weight: 800;
            padding: 16px 36px;
            border-radius: 10px;
            box-shadow: 0 8px 30px var(--gold-glow);
            transition: all 0.25s ease;
            cursor: pointer;
            border: none;
            position: relative;
            overflow: hidden;
        }

        .btn-luxury-gold::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 60%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            transform: skewX(-25deg);
            animation: shimmerSweep 3s infinite;
        }

        .btn-luxury-gold:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 36px rgba(212, 175, 55, 0.55);
        }

        .btn-luxury-glass {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: rgba(14, 21, 37, 0.65);
            border: 1px solid var(--border);
            color: var(--text-bright);
            font-size: 15px;
            font-weight: 700;
            padding: 16px 32px;
            border-radius: 10px;
            backdrop-filter: blur(12px);
            transition: all 0.25s ease;
            cursor: pointer;
        }

        .btn-luxury-glass:hover {
            border-color: var(--border-gold);
            background: rgba(20, 31, 54, 0.85);
            transform: translateY(-3px);
            color: var(--gold-200);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
        }

        /* ---------------- LIVE COUNTERS ---------------- */
        .stats-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
            max-width: 1000px;
            margin: 0 auto 60px;
            padding: 24px 30px;
            background: rgba(14, 21, 37, 0.45);
            border: 1px solid var(--border);
            border-radius: 14px;
            backdrop-filter: blur(16px);
        }

        .stat-box {
            text-align: center;
            border-right: 1px solid var(--border);
        }

        .stat-box:last-child {
            border-right: none;
        }

        .stat-number {
            font-size: 30px;
            font-weight: 800;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Cinzel', serif;
            letter-spacing: -0.5px;
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }

        /* ---------------- HERO REALISTIC INTERACTIVE PREVIEW ---------------- */
        .preview-wrapper {
            max-width: 1060px;
            margin: 0 auto;
            background: linear-gradient(180deg, rgba(20, 31, 54, 0.8) 0%, rgba(9, 14, 23, 0.95) 100%);
            border: 1px solid var(--border-gold);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 
                0 30px 80px -20px rgba(0, 0, 0, 0.9),
                0 0 50px rgba(212, 175, 55, 0.15);
        }

        .preview-window-bar {
            background: #080C14;
            padding: 14px 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
        }

        .preview-dots {
            display: flex;
            gap: 8px;
        }

        .preview-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .preview-dot.red { background: #EF4444; }
        .preview-dot.yellow { background: #F59E0B; }
        .preview-dot.green { background: #10B981; }

        .preview-window-title {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--gold-300);
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        /* Interactive Mode Switcher */
        .preview-tab-row {
            display: flex;
            background: rgba(5, 7, 11, 0.7);
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
        }

        .preview-tab-btn {
            flex: 1;
            background: transparent;
            border: none;
            padding: 14px 18px;
            color: var(--text-dim);
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.25s;
            border-bottom: 2px solid transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            white-space: nowrap;
        }

        .preview-tab-btn:hover {
            color: var(--text-bright);
            background: rgba(255, 255, 255, 0.02);
        }

        .preview-tab-btn.active {
            color: var(--gold-200);
            border-bottom: 2px solid var(--gold-400);
            background: rgba(212, 175, 55, 0.08);
        }

        .preview-content-grid {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 28px;
            padding: 32px;
            text-align: left;
            align-items: center;
        }

        .preview-media-frame {
            position: relative;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid var(--border);
            height: 320px;
            background: #000;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
        }

        .preview-media-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s ease, filter 0.6s ease;
        }

        .preview-media-frame:hover .preview-media-img {
            transform: scale(1.04);
        }

        .preview-overlay-badge {
            position: absolute;
            top: 16px;
            left: 16px;
            background: rgba(5, 7, 11, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-gold);
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
            color: var(--gold-200);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .preview-overlay-resolution {
            position: absolute;
            bottom: 16px;
            right: 16px;
            background: rgba(5, 7, 11, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(56, 189, 248, 0.4);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 800;
            color: #38BDF8;
            font-family: 'JetBrains Mono', monospace;
        }

        .preview-details-col {
            display: flex;
            flex-direction: column;
            gap: 18px;
        }

        .preview-details-col h4 {
            font-size: 20px;
            font-weight: 800;
            line-height: 1.3;
        }

        .preview-chip-row {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .preview-chip {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            color: var(--text-dim);
        }

        .preview-chip.gold {
            background: rgba(212, 175, 55, 0.12);
            border-color: var(--border-gold);
            color: var(--gold-200);
        }

        .preview-meter-wrap {
            background: rgba(5, 7, 11, 0.6);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
        }

        .preview-meter-header {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .preview-meter-bar {
            height: 8px;
            background: #1A243A;
            border-radius: 100px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .preview-meter-fill {
            height: 100%;
            width: 89%;
            background: var(--gold-gradient);
            border-radius: 100px;
            box-shadow: 0 0 12px rgba(212, 175, 55, 0.6);
        }

        .preview-meter-stats {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }

        /* ---------------- SECTION COMMON ---------------- */
        .section {
            max-width: 1240px;
            margin: 0 auto;
            padding: 110px 24px;
        }

        .section-header {
            text-align: center;
            max-width: 740px;
            margin: 0 auto 65px;
        }

        .section-tag {
            font-family: 'Cinzel', serif;
            font-size: 12px;
            font-weight: 700;
            color: var(--gold-300);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 12px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .section-tag::before, .section-tag::after {
            content: '◆';
            font-size: 8px;
            color: var(--gold-400);
        }

        .section-title {
            font-family: 'Cinzel', serif;
            font-size: 42px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 18px;
            line-height: 1.2;
        }

        .section-desc {
            font-size: 17px;
            color: var(--text-dim);
            line-height: 1.7;
        }

        /* ---------------- LUXURY REALISTIC PHOTOGRAPHY SHOWCASE ---------------- */
        .showcase-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 28px;
        }

        .showcase-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 18px;
            overflow: hidden;
            backdrop-filter: blur(16px);
            transition: all 0.35s ease;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .showcase-card:hover {
            transform: translateY(-6px);
            border-color: var(--border-gold);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(212, 175, 55, 0.15);
        }

        .showcase-img-wrap {
            height: 250px;
            overflow: hidden;
            position: relative;
        }

        .showcase-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .showcase-card:hover .showcase-img {
            transform: scale(1.06);
        }

        .showcase-img-gradient {
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, transparent 40%, rgba(14, 21, 37, 0.95) 100%);
        }

        .showcase-badge {
            position: absolute;
            top: 18px;
            left: 18px;
            background: rgba(5, 7, 11, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-gold);
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 800;
            color: var(--gold-200);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .showcase-body {
            padding: 28px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .showcase-body h3 {
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 12px;
            color: var(--text-bright);
        }

        .showcase-body p {
            font-size: 14px;
            color: var(--text-dim);
            line-height: 1.7;
            margin-bottom: 20px;
        }

        .showcase-meta-row {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 12px;
            font-family: 'JetBrains Mono', monospace;
            color: var(--gold-300);
            border-top: 1px solid var(--border);
            padding-top: 16px;
        }

        /* ---------------- LUXURY PRICING ---------------- */
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            align-items: stretch;
        }

        .pricing-card {
            background: rgba(14, 21, 37, 0.65);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 44px 34px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            backdrop-filter: blur(20px);
            transition: all 0.35s ease;
        }

        .pricing-card:hover {
            transform: translateY(-8px);
            border-color: var(--border-gold);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
        }

        .pricing-card.featured {
            background: linear-gradient(180deg, rgba(28, 41, 70, 0.75) 0%, rgba(14, 21, 37, 0.95) 100%);
            border: 2px solid var(--gold-400);
            box-shadow: 
                0 25px 70px rgba(0, 0, 0, 0.8),
                0 0 40px rgba(212, 175, 55, 0.2);
        }

        .featured-ribbon {
            position: absolute;
            top: -14px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--gold-gradient);
            color: #05070B;
            font-size: 11px;
            font-weight: 800;
            padding: 5px 16px;
            border-radius: 100px;
            letter-spacing: 1px;
            text-transform: uppercase;
            box-shadow: 0 4px 14px var(--gold-glow);
        }

        .plan-crown {
            font-size: 32px;
            margin-bottom: 12px;
        }

        .plan-name {
            font-family: 'Cinzel', serif;
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .plan-desc {
            font-size: 13px;
            color: var(--text-dim);
            margin-bottom: 24px;
            min-height: 40px;
            line-height: 1.6;
        }

        .plan-price-wrap {
            margin-bottom: 30px;
            display: flex;
            align-items: baseline;
            gap: 6px;
        }

        .plan-price {
            font-family: 'Cinzel', serif;
            font-size: 52px;
            font-weight: 800;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }

        .plan-term {
            font-size: 14px;
            color: var(--text-muted);
            font-weight: 700;
        }

        .plan-features {
            list-style: none;
            margin-bottom: 36px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .plan-feature-item {
            font-size: 14px;
            color: var(--text-bright);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .plan-feature-item span.icon-check {
            color: var(--gold-300);
            font-size: 16px;
        }

        .plan-btn {
            width: 100%;
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.25s;
            text-align: center;
            border: none;
            position: relative;
            overflow: hidden;
        }

        .plan-btn.solid {
            background: var(--gold-gradient);
            color: #05070B;
            box-shadow: 0 6px 20px var(--gold-glow);
        }

        .plan-btn.solid:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.5);
        }

        .plan-btn.outline {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border);
            color: var(--text-bright);
        }

        .plan-btn.outline:hover {
            border-color: var(--border-gold);
            background: rgba(212, 175, 55, 0.1);
            color: var(--gold-200);
            transform: translateY(-2px);
        }

        /* ---------------- LUXURY VIP TESTIMONIALS ---------------- */
        .testimonials-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 28px;
        }

        .testimonial-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 34px 28px;
            backdrop-filter: blur(16px);
            transition: all 0.3s;
        }

        .testimonial-card:hover {
            border-color: var(--border-gold);
            transform: translateY(-4px);
        }

        .testimonial-stars {
            color: var(--gold-400);
            font-size: 15px;
            margin-bottom: 16px;
            letter-spacing: 2px;
        }

        .testimonial-quote {
            font-size: 14px;
            color: var(--text-dim);
            line-height: 1.7;
            margin-bottom: 24px;
            font-style: italic;
        }

        .testimonial-user {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .testimonial-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--border-gold);
        }

        .testimonial-name {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-bright);
        }

        .testimonial-role {
            font-size: 12px;
            color: var(--gold-300);
            font-weight: 600;
        }

        /* ---------------- DIRECT DOWNLOAD BANNER ---------------- */
        .luxury-download-card {
            background: linear-gradient(135deg, rgba(20, 31, 54, 0.9) 0%, rgba(8, 12, 20, 0.95) 100%);
            border: 1px solid var(--border-gold);
            border-radius: 24px;
            padding: 60px 40px;
            text-align: center;
            max-width: 900px;
            margin: 0 auto;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.8), 0 0 50px rgba(212, 175, 55, 0.12);
            position: relative;
            overflow: hidden;
        }

        .luxury-download-card h3 {
            font-family: 'Cinzel', serif;
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 14px;
        }

        .luxury-download-card p {
            font-size: 16px;
            color: var(--text-dim);
            max-width: 620px;
            margin: 0 auto 32px;
            line-height: 1.7;
        }

        /* ---------------- FAQ ACCORDION ---------------- */
        .faq-accordion {
            max-width: 820px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .faq-item {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            transition: all 0.3s;
        }

        .faq-item.active {
            border-color: var(--border-gold);
        }

        .faq-question {
            padding: 22px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            color: var(--text-bright);
        }

        .faq-toggle-icon {
            font-size: 18px;
            color: var(--gold-400);
            transition: transform 0.3s;
        }

        .faq-item.active .faq-toggle-icon {
            transform: rotate(45deg);
        }

        .faq-answer {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.35s ease, padding 0.35s ease;
            padding: 0 28px;
            color: var(--text-dim);
            font-size: 14px;
            line-height: 1.7;
        }

        .faq-item.active .faq-answer {
            max-height: 250px;
            padding-bottom: 22px;
        }

        /* ---------------- FOOTER ---------------- */
        footer {
            border-top: 1px solid var(--border);
            padding: 60px 24px;
            background: #040609;
            font-size: 14px;
            color: var(--text-muted);
        }

        .footer-container {
            max-width: 1240px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 24px;
        }

        .footer-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .footer-links {
            display: flex;
            gap: 28px;
        }

        .footer-links a {
            transition: color 0.2s;
        }

        .footer-links a:hover {
            color: var(--gold-200);
        }

        /* ---------------- CHECKOUT MODAL ---------------- */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(3, 5, 8, 0.85);
            backdrop-filter: blur(16px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 20px;
        }

        .modal-card {
            background: #0B111E;
            border: 1px solid var(--border-gold);
            border-radius: 20px;
            width: 100%;
            max-width: 520px;
            padding: 36px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.9), 0 0 40px rgba(212, 175, 55, 0.2);
            position: relative;
            animation: modalFade 0.25s ease;
        }

        @keyframes modalFade {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }

        .modal-close {
            position: absolute;
            top: 22px;
            right: 22px;
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 20px;
            cursor: pointer;
            transition: color 0.2s;
        }

        .modal-close:hover {
            color: var(--gold-300);
        }

        .modal-title {
            font-family: 'Cinzel', serif;
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .modal-subtitle {
            font-size: 13px;
            color: var(--text-dim);
            margin-bottom: 24px;
        }

        .plan-summary-badge {
            background: rgba(14, 21, 37, 0.7);
            border: 1px solid var(--border-gold);
            border-radius: 10px;
            padding: 14px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 22px;
        }

        .plan-summary-title {
            font-weight: 700;
            font-size: 15px;
        }

        .plan-summary-price {
            font-family: 'Cinzel', serif;
            font-weight: 800;
            font-size: 18px;
            color: var(--gold-300);
        }

        .form-group {
            margin-bottom: 18px;
        }

        .form-label {
            display: block;
            font-size: 11px;
            font-weight: 700;
            color: var(--text-dim);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .form-input {
            width: 100%;
            background: #05070B;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 13px 16px;
            color: var(--text-bright);
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .form-input:focus {
            border-color: var(--gold-400);
            box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
        }

        .key-display-box {
            background: #05070B;
            border: 2px dashed var(--gold-400);
            border-radius: 12px;
            padding: 22px;
            text-align: center;
            margin: 24px 0;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.15);
        }

        .key-text {
            font-family: 'JetBrains Mono', monospace;
            font-size: 19px;
            font-weight: 800;
            color: #34D399;
            letter-spacing: 1px;
            word-break: break-all;
            margin-bottom: 14px;
        }

        .btn-copy-key {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-gold);
            color: var(--gold-200);
            padding: 9px 18px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-copy-key:hover {
            background: rgba(212, 175, 55, 0.2);
        }

        .activation-steps {
            background: rgba(14, 21, 37, 0.6);
            border-radius: 10px;
            padding: 16px 18px;
            font-size: 12px;
            color: var(--text-dim);
            margin-bottom: 22px;
            line-height: 1.8;
            border: 1px solid var(--border);
        }

        /* Responsive */
        @media (max-width: 900px) {
            .hero-title { font-size: 42px; }
            .preview-content-grid { grid-template-columns: 1fr; }
            .preview-media-frame { height: 240px; }
            .showcase-grid { grid-template-columns: 1fr; }
            .pricing-grid { grid-template-columns: 1fr; }
            .testimonials-grid { grid-template-columns: 1fr; }
            .stats-strip { grid-template-columns: repeat(2, 1fr); }
            .nav-links { display: none; }
        }
    </style>
</head>
<body>

    <!-- Ambient Glowing Orbs -->
    <div class="ambient-orb gold"></div>
    <div class="ambient-orb sapphire"></div>
    <div class="ambient-orb emerald"></div>
    <div class="noise-overlay"></div>

    <div class="content-layer">

        <!-- ---------------- NAVBAR ---------------- -->
        <nav class="navbar">
            <div class="nav-container">
                <a href="/" class="logo">
                    <span class="logo-crown">👑</span>
                    <span class="logo-text">Downloader Pro</span>
                    <span class="badge-edition">LUXURY EDITION</span>
                </a>
                <div class="nav-links">
                    <a href="#showcase" class="nav-link">Capabilities</a>
                    <a href="#experience" class="nav-link">Experience</a>
                    <a href="#pricing" class="nav-link">Licensing</a>
                    <a href="#reviews" class="nav-link">VIP Reviews</a>
                    <a href="#faq" class="nav-link">FAQ</a>
                </div>
                <a href="#pricing" class="nav-btn">
                    <span>👑</span> Unlock Pro Access
                </a>
            </div>
        </nav>

        <!-- ---------------- HERO SECTION ---------------- -->
        <section class="hero">
            <div class="hero-pill reveal">
                <span class="star-icon">★</span>
                The Definitive 4K HDR & Watermark-Free Downloader for Windows
            </div>

            <h1 class="hero-title reveal delay-1">
                Engineered for <span class="gold-accent">Pure Perfection</span> <br>
                and Uncompromised Quality.
            </h1>

            <p class="hero-subtitle reveal delay-2">
                Download master-grade 4K 60fps cinematic videos, extract TikTok streams with 100% of watermarks removed, batch archive full YouTube playlists, and convert to 320kbps audiophile MP3 sound.
            </p>

            <div class="hero-actions reveal delay-3">
                <a href="/download" class="btn-luxury-gold">
                    <span>⬇️</span> Download Installer for Windows (.exe)
                </a>
                <a href="#pricing" class="btn-luxury-glass">
                    <span>👑</span> View Pro Licenses
                </a>
            </div>

            <!-- Live Animated Counter Strip -->
            <div class="stats-strip reveal delay-4">
                <div class="stat-box">
                    <div class="stat-number" data-target="2840000">2,840,000+</div>
                    <div class="stat-label">Videos Downloaded</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">4K 60fps</div>
                    <div class="stat-label">Max Resolution</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">0%</div>
                    <div class="stat-label">TikTok Watermarks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">320 kbps</div>
                    <div class="stat-label">Studio Hi-Fi Audio</div>
                </div>
            </div>

            <!-- Realistic Interactive Live Mockup -->
            <div class="preview-wrapper reveal delay-4" id="experience">
                <div class="preview-window-bar">
                    <div class="preview-dots">
                        <div class="preview-dot red"></div>
                        <div class="preview-dot yellow"></div>
                        <div class="preview-dot green"></div>
                    </div>
                    <div class="preview-window-title">Downloader Pro v2.2 — Master Engine Active</div>
                    <div style="font-size: 11px; color: var(--gold-300); font-weight: 700;">PRO LICENSED</div>
                </div>

                <!-- Interactive Resolution / Mode Selector Tabs -->
                <div class="preview-tab-row">
                    <button class="preview-tab-btn active" onclick="switchPreviewTab('4k', this)">
                        <span>🌟</span> 4K HDR 60fps Cinema
                    </button>
                    <button class="preview-tab-btn" onclick="switchPreviewTab('tiktok', this)">
                        <span>📱</span> TikTok Clean Stream
                    </button>
                    <button class="preview-tab-btn" onclick="switchPreviewTab('audio', this)">
                        <span>🎵</span> 320kbps Studio Master
                    </button>
                    <button class="preview-tab-btn" onclick="switchPreviewTab('playlist', this)">
                        <span>🚀</span> Full Playlist Batch
                    </button>
                </div>

                <div class="preview-content-grid">
                    <div class="preview-media-frame">
                        <img id="previewImg" class="preview-media-img" src="https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=800&q=80" alt="4K Cinema Sensor">
                        <div class="preview-overlay-badge" id="previewBadge">4K UHD Master Stream</div>
                        <div class="preview-overlay-resolution" id="previewRes">3840 x 2160 • 60 FPS</div>
                    </div>

                    <div class="preview-details-col">
                        <h4 id="previewTitle">Cinema 4K Ultra HD Stream (HDR10 Rec.2020)</h4>
                        
                        <div class="preview-chip-row">
                            <span class="preview-chip gold">VP9 / AV1 60fps</span>
                            <span class="preview-chip">Multi-Thread Turbo</span>
                            <span class="preview-chip">Zero Compression Loss</span>
                        </div>

                        <div class="preview-meter-wrap">
                            <div class="preview-meter-header">
                                <span id="previewProgressTxt">Downloading: 89% Complete</span>
                                <span style="color: var(--gold-300);" id="previewSpeed">62.8 MB/s</span>
                            </div>
                            <div class="preview-meter-bar">
                                <div class="preview-meter-fill" id="previewBarFill"></div>
                            </div>
                            <div class="preview-meter-stats">
                                <span>3.4 GB / 3.8 GB</span>
                                <span>ETA: 00:06 Remaining</span>
                            </div>
                        </div>

                        <p style="font-size: 13px; color: var(--text-dim); line-height: 1.6;" id="previewDesc">
                            Preserves the complete dynamic color range, uncompressed audio channels, and ultra-smooth 60 frames per second directly to your local NVMe storage.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- ---------------- CAPABILITIES SHOWCASE WITH REALISTIC PHOTOS ---------------- -->
        <section class="section" id="showcase">
            <div class="section-header reveal">
                <div class="section-tag">Cinematic Engineering</div>
                <h2 class="section-title">Built for Those Who Demand the Best</h2>
                <p class="section-desc">Experience unmatched fidelity, zero watermarks, and raw multithreaded download horsepower.</p>
            </div>

            <div class="showcase-grid">
                <!-- Card 1: 4K Cinema -->
                <div class="showcase-card reveal">
                    <div class="showcase-img-wrap">
                        <img class="showcase-img" src="https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?auto=format&fit=crop&w=800&q=80" alt="Video Editing Timeline">
                        <div class="showcase-img-gradient"></div>
                        <div class="showcase-badge">ULTRA HD 4K & 2K</div>
                    </div>
                    <div class="showcase-body">
                        <h3>Master 4K & 2K 60fps Extraction</h3>
                        <p>Download full cinematic 4K UHD (2160p) and 2K QHD (1440p) with native high frame-rate rendering. Perfect for luxury home theaters, archival collections, and video editors.</p>
                        <div class="showcase-meta-row">
                            <span>✦ 3840x2160 Native</span>
                            <span>✦ HDR10 Color</span>
                            <span>✦ High Bitrate AV1</span>
                        </div>
                    </div>
                </div>

                <!-- Card 2: TikTok Clean Extractor -->
                <div class="showcase-card reveal delay-1">
                    <div class="showcase-img-wrap">
                        <img class="showcase-img" src="https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=800&q=80" alt="TikTok Creator Setup">
                        <div class="showcase-img-gradient"></div>
                        <div class="showcase-badge">ZERO WATERMARKS</div>
                    </div>
                    <div class="showcase-body">
                        <h3>Pristine Clean TikTok Streams</h3>
                        <p>Directly taps into the origin server feed before TikTok embeds bouncing logo watermarks or user tags. Obtain pristine, distraction-free video clips for repurposing and offline vaults.</p>
                        <div class="showcase-meta-row">
                            <span>✦ 100% Watermark-Free</span>
                            <span>✦ Full Resolution</span>
                            <span>✦ Hi-Fi Audio</span>
                        </div>
                    </div>
                </div>

                <!-- Card 3: Studio Audio Mastering -->
                <div class="showcase-card reveal delay-2">
                    <div class="showcase-img-wrap">
                        <img class="showcase-img" src="https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=800&q=80" alt="Audio Mastering Console">
                        <div class="showcase-img-gradient"></div>
                        <div class="showcase-badge">STUDIO AUDIO 320 KBPS</div>
                    </div>
                    <div class="showcase-body">
                        <h3>Studio-Grade 320kbps MP3 & M4A</h3>
                        <p>Extract uncompressed audio tracks directly from videos. Automatically encoded with studio-grade 320kbps MP3 or lossless M4A, complete with embedded metadata and album art.</p>
                        <div class="showcase-meta-row">
                            <span>✦ 320 kbps Constant</span>
                            <span>✦ 48 kHz Sample Rate</span>
                            <span>✦ ID3 Tagging</span>
                        </div>
                    </div>
                </div>

                <!-- Card 4: Playlist Batch Acceleration -->
                <div class="showcase-card reveal delay-3">
                    <div class="showcase-img-wrap">
                        <img class="showcase-img" src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80" alt="Workstation Command Setup">
                        <div class="showcase-img-gradient"></div>
                        <div class="showcase-badge">PLAYLIST QUEUE</div>
                    </div>
                    <div class="showcase-body">
                        <h3>Unlimited Full Playlist Archival</h3>
                        <p>Paste any YouTube playlist link and batch-download dozens or hundreds of videos in a single automated process. Includes automated sequential numbering and smart retry acceleration.</p>
                        <div class="showcase-meta-row">
                            <span>✦ 500+ Items at Once</span>
                            <span>✦ Parallel Threads</span>
                            <span>✦ Auto-Numbered</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ---------------- LUXURY PRICING SECTION ---------------- -->
        <section class="section" id="pricing">
            <div class="section-header reveal">
                <div class="section-tag">Royal Entitlements</div>
                <h2 class="section-title">Select Your Pro License</h2>
                <p class="section-desc">Instant online key generation. Mathematically verified cryptographic signatures for 100% guaranteed activation on any computer.</p>
            </div>

            <div class="pricing-grid">
                <!-- Monthly -->
                <div class="pricing-card reveal">
                    <div>
                        <div class="plan-crown">👑</div>
                        <div class="plan-name">Monthly Pass</div>
                        <div class="plan-desc">Experience full Pro capabilities with complete month-to-month flexibility.</div>
                        <div class="plan-price-wrap">
                            <span class="plan-price">$9.99</span>
                            <span class="plan-term">/ month</span>
                        </div>

                        <ul class="plan-features">
                            <li class="plan-feature-item"><span class="icon-check">✦</span> 1 PC Hardware Bound Activation</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Unlimited 4K & 2K 60fps Downloads</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> TikTok Clean Extractor (No Watermark)</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Unlimited Playlist Batch Downloads</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Cancel Anytime with 1 Click</li>
                        </ul>
                    </div>

                    <button class="plan-btn outline" onclick="openCheckout('pro_monthly', 'Monthly Pass', '$9.99 / month')">
                        Acquire Monthly Pass
                    </button>
                </div>

                <!-- Annual -->
                <div class="pricing-card featured reveal delay-1">
                    <div class="featured-ribbon">⭐ Most Popular Privilege</div>
                    <div>
                        <div class="plan-crown">👑</div>
                        <div class="plan-name">Annual Master</div>
                        <div class="plan-desc">Save 75% compared to monthly. The gold standard for creators and power collectors.</div>
                        <div class="plan-price-wrap">
                            <span class="plan-price">$29.99</span>
                            <span class="plan-term">/ year</span>
                        </div>

                        <ul class="plan-features">
                            <li class="plan-feature-item"><span class="icon-check">✦</span> <strong>2 PCs Hardware Bound Activation</strong></li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Unlimited 4K & 2K 60fps Downloads</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> TikTok Zero-Watermark Stream Extractor</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Full Playlist Multi-Thread Processing</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Studio 320kbps MP3 Audio Extraction</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Priority Future Updates & Features</li>
                        </ul>
                    </div>

                    <button class="plan-btn solid" onclick="openCheckout('pro_yearly', 'Annual Master License', '$29.99 / year')">
                        👑 Acquire Annual License
                    </button>
                </div>

                <!-- Lifetime -->
                <div class="pricing-card reveal delay-2">
                    <div>
                        <div class="plan-crown">💎</div>
                        <div class="plan-name">Lifetime Royalty</div>
                        <div class="plan-desc">Pay once, own forever. The ultimate investment in permanent media archival freedom.</div>
                        <div class="plan-price-wrap">
                            <span class="plan-price">$49.99</span>
                            <span class="plan-term">/ one-time</span>
                        </div>

                        <ul class="plan-features">
                            <li class="plan-feature-item"><span class="icon-check">✦</span> <strong>3 PCs Hardware Bound Activation</strong></li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Pay Once • Own Forever (No Recurring Fees)</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Complete Unrestricted Pro Access</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Free Lifetime Future Major Upgrades</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Seamless License Transfer Between PCs</li>
                            <li class="plan-feature-item"><span class="icon-check">✦</span> Dedicated VIP 24/7 Priority Support</li>
                        </ul>
                    </div>

                    <button class="plan-btn outline" onclick="openCheckout('pro_lifetime', 'Lifetime Royalty License', '$49.99 one-time')">
                        💎 Acquire Lifetime Royalty
                    </button>
                </div>
            </div>
        </section>

        <!-- ---------------- LUXURY VIP REVIEWS ---------------- -->
        <section class="section" id="reviews" style="background: rgba(14, 21, 37, 0.35); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);">
            <div class="section-header reveal">
                <div class="section-tag">Verified Acclaim</div>
                <h2 class="section-title">Endorsed by Master Creators</h2>
                <p class="section-desc">Read how industry professionals rely on Downloader Pro for their media production and digital vaults.</p>
            </div>

            <div class="testimonials-grid">
                <div class="testimonial-card reveal">
                    <div class="testimonial-stars">★★★★★</div>
                    <p class="testimonial-quote">"The 4K 60fps fidelity is untouched. As a documentary colorist, I need true source quality without compression artifacts. Downloader Pro delivers the real raw stream every single time."</p>
                    <div class="testimonial-user">
                        <img class="testimonial-avatar" src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80" alt="Marcus Vance">
                        <div>
                            <div class="testimonial-name">Marcus Vance</div>
                            <div class="testimonial-role">Senior Colorist & Filmmaker</div>
                        </div>
                    </div>
                </div>

                <div class="testimonial-card reveal delay-1">
                    <div class="testimonial-stars">★★★★★</div>
                    <p class="testimonial-quote">"The TikTok clean stream extractor is incredible. It strips 100% of the watermarks cleanly and preserves the original audio track. It saved our marketing agency countless hours."</p>
                    <div class="testimonial-user">
                        <img class="testimonial-avatar" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80" alt="Elena Rostova">
                        <div>
                            <div class="testimonial-name">Elena Rostova</div>
                            <div class="testimonial-role">Creative Media Director</div>
                        </div>
                    </div>
                </div>

                <div class="testimonial-card reveal delay-2">
                    <div class="testimonial-stars">★★★★★</div>
                    <p class="testimonial-quote">"I archived my entire music and educational playlist collection with hundreds of videos with one click. Multi-thread speeds maxed out my 1 Gbps fiber. Best investment I've made."</p>
                    <div class="testimonial-user">
                        <img class="testimonial-avatar" src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80" alt="David Sterling">
                        <div>
                            <div class="testimonial-name">David Sterling</div>
                            <div class="testimonial-role">Digital Audio Archivist</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ---------------- DIRECT INSTALLER DOWNLOAD CARD ---------------- -->
        <section class="section" id="download">
            <div class="luxury-download-card reveal">
                <div style="font-size: 48px; margin-bottom: 12px;">⚡</div>
                <h3>Experience Downloader Pro on Windows</h3>
                <p>Download the official standalone installation suite for Windows 10 and Windows 11 (64-bit). No third-party bloatware, no browser extensions, 100% pure high-performance native code.</p>
                
                <a href="/download" class="btn-luxury-gold" style="font-size: 16px; padding: 18px 42px;">
                    <span>⬇️</span> Download DownloaderPro_Setup.exe (~90 MB)
                </a>

                <div style="display: flex; justify-content: center; gap: 24px; margin-top: 28px; font-size: 13px; color: var(--text-muted); flex-wrap: wrap;">
                    <span>🛡️ SHA-256 Digitally Signed</span>
                    <span>•</span>
                    <span>💻 Windows 10 & 11 64-bit</span>
                    <span>•</span>
                    <span>⚡ Multi-Thread Hardware Acceleration</span>
                </div>
            </div>
        </section>

        <!-- ---------------- FAQ ACCORDION ---------------- -->
        <section class="section" id="faq">
            <div class="section-header reveal">
                <div class="section-tag">Inquiries</div>
                <h2 class="section-title">Frequently Asked Questions</h2>
            </div>

            <div class="faq-accordion reveal">
                <div class="faq-item active">
                    <div class="faq-question" onclick="toggleFaq(this)">
                        <span>How do I activate my Pro plan on my computer?</span>
                        <span class="faq-toggle-icon">✕</span>
                    </div>
                    <div class="faq-answer">
                        After ordering your plan on this website, your cryptographically signed license key (e.g. <code>MDP-LFT-XXXX-XXXX-XXXX</code>) is generated and displayed on your screen instantly. Open Downloader Pro on your PC, click the crown icon 👑 in the header or Settings, paste your key, and click Activate. Pro unlocks immediately.
                    </div>
                </div>

                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">
                        <span>Can I transfer my license to a new PC?</span>
                        <span class="faq-toggle-icon">+</span>
                    </div>
                    <div class="faq-answer">
                        Yes! Open Downloader Pro on your old PC, navigate to Settings, and click <strong>"🔌 Deactivate / Transfer PC"</strong>. This immediately releases your activation slot so you can activate your key on your new machine.
                    </div>
                </div>

                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">
                        <span>How does the TikTok clean extractor remove watermarks?</span>
                        <span class="faq-toggle-icon">+</span>
                    </div>
                    <div class="faq-answer">
                        Downloader Pro connects directly to the high-bitrate raw content delivery server before TikTok's encoding engine overlays the watermark and username. You receive the exact original high-definition video file.
                    </div>
                </div>

                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">
                        <span>Does the license work offline?</span>
                        <span class="faq-toggle-icon">+</span>
                    </div>
                    <div class="faq-answer">
                        Yes. Every key issued by Downloader Pro contains a mathematical HMAC-SHA256 signature bound to your machine hardware. Once activated, the app validates offline with 100% accuracy without needing a constant internet connection to the license server.
                    </div>
                </div>
            </div>
        </section>

        <!-- ---------------- FOOTER ---------------- -->
        <footer>
            <div class="footer-container">
                <div class="footer-brand">
                    <span style="font-size: 20px;">👑</span>
                    <span class="logo-text">Downloader Pro</span>
                    <span style="font-size: 13px; color: var(--text-muted); font-weight: 500;">• prodownloader.site • © 2026. All rights reserved.</span>
                </div>

                <div class="footer-links">
                    <a href="#showcase">Capabilities</a>
                    <a href="#pricing">Licensing</a>
                    <a href="/download">Download</a>
                    <a href="/admin" target="_blank" style="color: var(--gold-300); font-weight: 700;">🔒 Seller Admin</a>
                </div>
            </div>
        </footer>

    </div>

    <!-- ---------------- CHECKOUT MODAL ---------------- -->
    <div class="modal-overlay" id="checkoutModal">
        <div class="modal-card">
            <button class="modal-close" onclick="closeCheckout()">✕</button>

            <!-- Step 1: Input Form -->
            <div id="checkoutFormStep">
                <div style="font-size: 32px; margin-bottom: 8px;">👑</div>
                <h3 class="modal-title">Acquire License Key</h3>
                <p class="modal-subtitle">Instant cryptographic key issuance directly on your screen.</p>

                <div class="plan-summary-badge">
                    <span class="plan-summary-title" id="mPlanTitle">Annual Master License</span>
                    <span class="plan-summary-price" id="mPlanPrice">$29.99 / year</span>
                </div>

                <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <input type="text" class="form-input" id="cName" placeholder="e.g. Alexander Vance">
                </div>

                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" class="form-input" id="cEmail" placeholder="e.g. alexander@example.com">
                </div>

                <button class="btn-luxury-gold" style="width: 100%; justify-content: center; margin-top: 14px;" id="btnSubmitOrder" onclick="processOrder()">
                    👑 Instant Order & Mint License Key
                </button>
            </div>

            <!-- Step 2: Key Generated Success -->
            <div id="checkoutSuccessStep" style="display: none; text-align: center;">
                <div style="font-size: 42px; margin-bottom: 8px;">🎉</div>
                <h3 class="modal-title" style="color: #34D399;">Order Confirmed</h3>
                <p class="modal-subtitle">Your cryptographic license key has been minted and registered.</p>

                <div class="key-display-box">
                    <div style="font-size: 11px; text-transform: uppercase; color: var(--gold-300); font-weight: 800; letter-spacing: 1px; margin-bottom: 8px;">Your Verified Pro Key:</div>
                    <div class="key-text" id="dispKey">MDP-LFT-XXXX-XXXX-XXXX</div>
                    <button class="btn-copy-key" id="btnCopyResult" onclick="copyResultKey()">📋 Copy License Key</button>
                </div>

                <div class="activation-steps" style="text-align: left;">
                    <strong style="color: var(--text-bright);">How to Activate in 3 Seconds:</strong><br>
                    1. Download & launch <strong>Downloader Pro</strong> below.<br>
                    2. Click the crown icon <strong>👑</strong> in the app header or Settings.<br>
                    3. Paste your key and click <strong>Activate Pro License</strong>.
                </div>

                <a href="/download" class="btn-luxury-gold" style="width: 100%; justify-content: center; padding: 14px;">
                    ⬇️ Download Downloader Pro Suite
                </a>
            </div>
        </div>
    </div>

    <!-- ---------------- JAVASCRIPT: SCROLL REVEAL & INTERACTIVITY ---------------- -->
    <script>
        // Scroll-triggered Reveal Animations
        const revealElements = document.querySelectorAll('.reveal');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, { threshold: 0.12 });

        revealElements.forEach(el => observer.observe(el));

        // Interactive Live Preview Switcher Data
        const previewModes = {
            '4k': {
                img: 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=800&q=80',
                badge: '4K UHD Cinema Stream',
                res: '3840 x 2160 • 60 FPS',
                title: 'Cinema 4K Ultra HD Stream (HDR10 Rec.2020)',
                progressTxt: 'Downloading: 89% Complete',
                speed: '62.8 MB/s',
                fill: '89%',
                desc: 'Preserves the complete dynamic color range, uncompressed audio channels, and ultra-smooth 60 frames per second directly to your local NVMe storage.'
            },
            'tiktok': {
                img: 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=800&q=80',
                badge: 'Clean Origin Stream',
                res: '1080 x 1920 • Clean',
                title: 'TikTok Clean Extractor (Zero Watermarks)',
                progressTxt: 'Extracting: 100% Complete',
                speed: '34.2 MB/s',
                fill: '100%',
                desc: 'Taps directly into the origin content delivery stream before TikTok applies bouncing logos or user watermark overlays.'
            },
            'audio': {
                img: 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=800&q=80',
                badge: 'Studio Mastering Feed',
                res: '320 kbps • 48 kHz',
                title: 'Audiophile 320kbps MP3 / Hi-Fi M4A',
                progressTxt: 'Mastering Audio: 95% Complete',
                speed: '41.5 MB/s',
                fill: '95%',
                desc: 'Extracts the original audio stream and encodes with constant 320kbps studio bitrate with embedded album art and full ID3 metadata.'
            },
            'playlist': {
                img: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80',
                badge: 'Multi-Thread Batch Queue',
                res: 'Batch 142 / 142 Videos',
                title: 'Full Playlist Multi-Thread Turbo Queue',
                progressTxt: 'Queue Progress: 76% Complete',
                speed: '78.4 MB/s',
                fill: '76%',
                desc: 'Queues and downloads entire series, music albums, or educational courses at maximum fiber speed with automated track numbering.'
            }
        };

        function switchPreviewTab(mode, btn) {
            document.querySelectorAll('.preview-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const data = previewModes[mode];
            if (!data) return;

            const img = document.getElementById('previewImg');
            img.style.opacity = '0.3';
            setTimeout(() => {
                img.src = data.img;
                img.style.opacity = '1';
            }, 180);

            document.getElementById('previewBadge').innerText = data.badge;
            document.getElementById('previewRes').innerText = data.res;
            document.getElementById('previewTitle').innerText = data.title;
            document.getElementById('previewProgressTxt').innerText = data.progressTxt;
            document.getElementById('previewSpeed').innerText = data.speed;
            document.getElementById('previewBarFill').style.width = data.fill;
            document.getElementById('previewDesc').innerText = data.desc;
        }

        // FAQ Accordion
        function toggleFaq(el) {
            const item = el.parentElement;
            const icon = el.querySelector('.faq-toggle-icon');
            const isActive = item.classList.contains('active');

            document.querySelectorAll('.faq-item').forEach(i => {
                i.classList.remove('active');
                i.querySelector('.faq-toggle-icon').innerText = '+';
            });

            if (!isActive) {
                item.classList.add('active');
                icon.innerText = '✕';
            }
        }

        // Checkout Modal & API
        let selectedPlan = 'pro_yearly';

        function openCheckout(plan, title, price) {
            selectedPlan = plan;
            document.getElementById('mPlanTitle').innerText = title;
            document.getElementById('mPlanPrice').innerText = price;
            document.getElementById('checkoutFormStep').style.display = 'block';
            document.getElementById('checkoutSuccessStep').style.display = 'none';
            document.getElementById('checkoutModal').style.display = 'flex';
        }

        function closeCheckout() {
            document.getElementById('checkoutModal').style.display = 'none';
        }

        function processOrder() {
            const name = document.getElementById('cName').value.trim() || 'Valued Customer';
            const email = document.getElementById('cEmail').value.trim() || '';
            const btn = document.getElementById('btnSubmitOrder');

            btn.disabled = true;
            btn.innerText = '⏳ Minting Cryptographic Key...';

            fetch('/api/v1/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    plan: selectedPlan,
                    name: name,
                    email: email
                })
            })
            .then(res => res.json())
            .then(data => {
                btn.disabled = false;
                btn.innerText = '👑 Instant Order & Mint License Key';

                if (data.status === 'success') {
                    document.getElementById('dispKey').innerText = data.license_key;
                    document.getElementById('checkoutFormStep').style.display = 'none';
                    document.getElementById('checkoutSuccessStep').style.display = 'block';
                } else {
                    alert('Order could not be processed. Please try again.');
                }
            })
            .catch(err => {
                btn.disabled = false;
                btn.innerText = '👑 Instant Order & Mint License Key';
                alert('Connection error: ' + err);
            });
        }

        function copyResultKey() {
            const key = document.getElementById('dispKey').innerText;
            navigator.clipboard.writeText(key).then(() => {
                const btn = document.getElementById('btnCopyResult');
                btn.innerText = '✔ Copied to Clipboard!';
                btn.style.color = '#34D399';
                setTimeout(() => {
                    btn.innerText = '📋 Copy License Key';
                    btn.style.color = 'inherit';
                }, 2000);
            });
        }

        // Close on clicking backdrop
        document.getElementById('checkoutModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeCheckout();
            }
        });
    </script>
</body>
</html>
"""
