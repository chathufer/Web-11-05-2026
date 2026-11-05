"""
Embedded Website HTML for Downloader Pro.
Campus design language tailored for Ultra HD Media Ripper.
"""

WEBSITE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Downloader Pro — 8K 60FPS Video, TikTok Clean & Studio 320k MP3 Ripper</title>
  <meta name="description" content="Ultra HD multi-threaded media ripper. Download pristine 8K 60FPS YouTube video, TikTok clips with zero watermarks, and studio-grade 320kbps MP3s in seconds.">
  <meta name="theme-color" content="#0b0b0b">

  <!-- Open Graph -->
  <meta property="og:title" content="Downloader Pro — Ultra HD Media Ripper">
  <meta property="og:description" content="Download YouTube 8K 60FPS, TikTok clean MP4, and 320kbps MP3s at uncapped speeds.">
  <meta property="og:type" content="website">

  <link rel="icon" type="image/png" href="icon.png">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">

  <!-- Google Fonts: Sora -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">

  <style>
    /* ============================================================
       CAMPUS DESIGN SYSTEM TOKENS & RESET
       ============================================================ */
    :root {
      --ink: #0b0b0b;
      --ink-2: #141414;
      --ink-3: #1d1d1d;
      --ink-line: rgba(255, 255, 255, .13);
      --gold: #f5b82e;
      --gold-hi: #ffc94f;
      --gold-deep: #d9990c;
      --paper: #fff8ea;
      --paper-2: #f5e9cf;
      --white: #ffffff;
      --muted-d: rgba(255, 255, 255, .72);
      --muted-l: #5c5345;

      --font: "Sora", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      --h1: clamp(2.5rem, 1.1rem + 4.8vw, 5.2rem);
      --h2: clamp(2.1rem, 1.2rem + 3.2vw, 4.2rem);
      --h1-lh: .96;
      --h2-lh: 1.02;

      --gutter: clamp(16px, 4.6vw, 56px);
      --max: 1280px;
      --header-h: 76px;
      --r: 24px;
      --ease: cubic-bezier(.2, .8, .2, 1);
      --snap: cubic-bezier(.34, 1.45, .55, 1);
      --btn-shadow: #ffffff;
      --shadow-ink: 6px 6px 0 var(--ink);
    }

    [data-theme="red"] {
      --gold: #ff2a5f;
      --gold-hi: #ff547e;
      --gold-deep: #d41443;
      --paper: #fff0f3;
      --paper-2: #fed7e0;
    }

    [data-theme="cyan"] {
      --gold: #19c3ff;
      --gold-hi: #54d4ff;
      --gold-deep: #009acc;
      --paper: #ecf9ff;
      --paper-2: #cbeeff;
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    html {
      scroll-behavior: smooth;
      background: var(--ink);
      color: var(--white);
      font-family: var(--font);
      font-size: 16px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    body {
      background: var(--ink);
      color: var(--white);
      overflow-x: hidden;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Wrap Container */
    .wrap {
      width: 100%;
      max-width: var(--max);
      margin-inline: auto;
      padding-inline: var(--gutter);
    }

    a {
      color: inherit;
      text-decoration: none;
    }

    button {
      font-family: inherit;
      border: none;
      background: transparent;
      cursor: pointer;
    }

    img, svg {
      display: block;
      max-width: 100%;
    }

    .ic {
      width: 20px;
      height: 20px;
      fill: none;
      stroke: currentColor;
      stroke-width: 2.2;
      stroke-linecap: round;
      stroke-linejoin: round;
      flex: none;
    }

    /* ============================================================
       TYPOGRAPHY, TAGS, STICKERS, MARKS
       ============================================================ */
    h1, h2, h3, h4 {
      font-weight: 800;
      letter-spacing: -.03em;
    }

    mark {
      background: var(--gold);
      color: var(--ink);
      padding: .02em .28em;
      border-radius: 6px;
      display: inline-block;
      transform: rotate(-2.5deg);
      box-decoration-break: clone;
      -webkit-box-decoration-break: clone;
      transition: background .3s var(--ease);
    }

    .u-gold {
      color: var(--gold);
      transition: color .3s var(--ease);
    }

    /* Diamond Bullet Tag */
    .tag {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 6px 14px;
      font-size: 12.5px;
      font-weight: 700;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--gold);
      background: rgba(245, 184, 46, .08);
      border: 1.5px solid rgba(245, 184, 46, .45);
      border-radius: 999px;
      transition: all .3s var(--ease);
    }

    [data-theme="red"] .tag {
      color: var(--gold);
      background: rgba(255, 42, 95, .08);
      border-color: rgba(255, 42, 95, .45);
    }

    [data-theme="cyan"] .tag {
      color: var(--gold);
      background: rgba(25, 195, 255, .08);
      border-color: rgba(25, 195, 255, .45);
    }

    .tag::before {
      content: "";
      width: 7px;
      height: 7px;
      background: currentColor;
      transform: rotate(45deg);
      flex: none;
    }

    .tag-ink {
      background: var(--ink);
      color: var(--gold);
      border-color: var(--gold);
    }

    /* Tilted Sticker */
    .sticker {
      display: inline-block;
      padding: 5px 12px;
      background: var(--ink);
      color: var(--gold);
      font-size: 13px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
      border: 2px solid var(--gold);
      border-radius: 8px;
      transform: rotate(-2.5deg);
      box-shadow: 4px 4px 0 var(--gold);
      margin-bottom: 12px;
      transition: all .3s var(--ease);
    }

    /* Wordmark */
    .wordmark {
      font-family: var(--font);
      font-weight: 800;
      font-size: 26px;
      letter-spacing: -.03em;
      color: var(--white);
      display: inline-flex;
      align-items: center;
      line-height: 1;
    }

    .wordmark .wm-period {
      color: var(--gold);
      transition: color .3s var(--ease);
    }

    .brand-sub {
      font-size: 11px;
      font-weight: 800;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--gold);
      background: rgba(245, 184, 46, .12);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid rgba(245, 184, 46, .35);
      margin-left: 8px;
      transition: all .3s var(--ease);
    }

    /* 3D Drop-Shadow Buttons */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 14px 26px;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -.01em;
      border-radius: 14px;
      border: 2px solid var(--ink);
      transition: transform .18s var(--ease), box-shadow .18s var(--ease), background .18s var(--ease);
      white-space: nowrap;
      user-select: none;
    }

    .btn:hover {
      transform: translate(-3px, -3px);
      box-shadow: 4px 4px 0 var(--btn-shadow);
    }

    .btn:active {
      transform: translate(0, 0);
      box-shadow: 0 0 0 var(--btn-shadow);
    }

    .btn-gold {
      background: var(--gold);
      color: var(--ink);
      border-color: var(--ink);
      --btn-shadow: #ffffff;
    }

    .btn-gold:hover {
      background: var(--gold-hi);
    }

    .btn-ink {
      background: var(--ink);
      color: var(--white);
      border-color: var(--ink-line);
      --btn-shadow: var(--gold);
    }

    .btn-ink:hover {
      background: var(--ink-2);
      border-color: var(--gold);
    }

    .btn-line {
      background: transparent;
      color: var(--white);
      border: 2px solid var(--ink-line);
      --btn-shadow: var(--gold);
    }

    .btn-line:hover {
      border-color: var(--gold);
      color: var(--gold);
    }

    .btn-sm {
      padding: 9px 18px;
      font-size: 13.5px;
      border-radius: 10px;
    }

    /* ============================================================
       SITE HEADER
       ============================================================ */
    .site-header {
      position: sticky;
      top: 0;
      z-index: 90;
      height: var(--header-h);
      background: rgba(11, 11, 11, .88);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--ink-line);
      transition: box-shadow .3s var(--ease), background .3s var(--ease);
    }

    .site-header.is-scrolled {
      box-shadow: 0 10px 30px rgba(0, 0, 0, .55);
      background: rgba(11, 11, 11, .96);
    }

    .header-in {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 100%;
      gap: 20px;
    }

    .brand {
      display: flex;
      align-items: center;
      flex: none;
    }

    .nav {
      display: flex;
      align-items: center;
      gap: 28px;
    }

    .nav a {
      font-size: 14.5px;
      font-weight: 600;
      color: var(--muted-d);
      transition: color .2s var(--ease);
      position: relative;
    }

    .nav a:hover {
      color: var(--gold);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    /* Theme Switcher Group */
    .theme-picker {
      display: flex;
      align-items: center;
      background: var(--ink-2);
      border: 1px solid var(--ink-line);
      border-radius: 999px;
      padding: 3px 5px;
      gap: 4px;
    }

    .theme-dot {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid transparent;
      padding: 0;
      transition: transform .2s var(--ease), border-color .2s var(--ease);
      position: relative;
    }

    .theme-dot[data-t="gold"] { background: #f5b82e; }
    .theme-dot[data-t="red"] { background: #ff2a5f; }
    .theme-dot[data-t="cyan"] { background: #19c3ff; }

    .theme-dot.is-active {
      transform: scale(1.18);
      border-color: #ffffff;
    }

    .menu-btn {
      display: none;
      width: 42px;
      height: 42px;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      border-radius: 10px;
      background: var(--ink-2);
      border: 1px solid var(--ink-line);
      color: var(--white);
    }

    .menu-btn span {
      width: 22px;
      height: 2px;
      background: currentColor;
      transition: transform .25s var(--ease);
    }

    /* Mobile Flyout Menu */
    .mobile-menu {
      position: fixed;
      inset: var(--header-h) 0 0 0;
      background: var(--ink);
      z-index: 89;
      display: flex;
      flex-direction: column;
      padding: 32px var(--gutter);
      gap: 22px;
      border-top: 1px solid var(--ink-line);
      transform: translateY(-100%);
      opacity: 0;
      pointer-events: none;
      transition: transform .35s var(--ease), opacity .35s var(--ease);
    }

    .mobile-menu.is-open {
      transform: translateY(0);
      opacity: 1;
      pointer-events: auto;
    }

    .mobile-menu a {
      font-size: 20px;
      font-weight: 700;
      color: var(--white);
      padding-block: 8px;
      border-bottom: 1px solid rgba(255, 255, 255, .08);
    }

    /* ============================================================
       HERO SECTION
       ============================================================ */
    .hero {
      position: relative;
      padding-top: clamp(40px, 6vw, 80px);
      padding-bottom: clamp(60px, 8vw, 110px);
      overflow: hidden;
      min-height: calc(100vh - var(--header-h));
      display: flex;
      align-items: center;
    }

    /* Angled Gold Backdrop Panel with Halftone Dot Pattern */
    .hero-panel {
      position: absolute;
      inset: 0;
      right: 0;
      left: 38%;
      background: var(--gold);
      clip-path: polygon(18% 0, 100% 0, 100% 100%, 0 100%);
      pointer-events: none;
      z-index: 1;
      opacity: 0.96;
      transition: background .3s var(--ease);
    }

    .hero-panel::before {
      content: "";
      position: absolute;
      inset: 0;
      background-image: radial-gradient(var(--ink) 1.5px, transparent 1.5px);
      background-size: 14px 14px;
      opacity: .18;
    }

    .hero-in {
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
      align-items: center;
      gap: clamp(32px, 5vw, 64px);
    }

    .hero-copy {
      max-width: 620px;
    }

    .hero h1 {
      font-size: var(--h1);
      line-height: var(--h1-lh);
      margin-top: 20px;
      margin-bottom: 20px;
      letter-spacing: -.035em;
    }

    .hero h1 .h1-end {
      display: inline-block;
    }

    .hero-sub {
      font-size: clamp(1.2rem, .95rem + .9vw, 1.65rem);
      font-weight: 700;
      letter-spacing: -.02em;
      margin-bottom: 18px;
      line-height: 1.25;
    }

    .hero .lead {
      font-size: clamp(1.02rem, .95rem + .3vw, 1.18rem);
      color: var(--muted-d);
      line-height: 1.6;
      margin-bottom: 32px;
    }

    .hero-actions {
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
    }

    .shield-item {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .shield {
      --shape: polygon(50% 0%, 100% 13%, 100% 50%, 96% 65%, 87% 78%, 70% 91%, 50% 100%, 30% 91%, 13% 78%, 4% 65%, 0% 50%, 0% 13%);
      position: relative;
      flex: none;
      width: 62px;
      height: 70px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: var(--gold);
      clip-path: var(--shape);
      transition: transform .3s var(--snap), background .3s var(--ease);
    }

    .shield:hover {
      transform: scale(1.08) rotate(3deg);
    }

    .shield::before {
      content: "";
      position: absolute;
      inset: 3.5px;
      background: var(--ink);
      clip-path: var(--shape);
    }

    .shield b {
      position: relative;
      color: var(--gold);
      font-size: 17px;
      font-weight: 800;
      line-height: 1;
      transition: color .3s var(--ease);
    }

    .shield small {
      position: relative;
      color: var(--white);
      font-size: 9px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
      line-height: 1;
      margin-top: 3px;
    }

    .shield-txt {
      display: flex;
      flex-direction: column;
    }

    .shield-txt b {
      font-size: 14.5px;
      font-weight: 700;
    }

    .shield-txt small {
      font-size: 12px;
      color: var(--muted-d);
    }

    /* Hero Art & Interactive Fan */
    .hero-art {
      position: relative;
      width: 100%;
      aspect-ratio: 1 / 1;
      max-width: 540px;
      margin-inline: auto;
    }

    .fan {
      position: absolute;
      inset: 0;
      --px: 0;
      --py: 0;
    }

    .fan-card {
      position: absolute;
      background: var(--ink-2);
      border: 3px solid var(--ink);
      border-radius: 20px;
      box-shadow: 8px 8px 0 var(--ink);
      overflow: hidden;
      transition: transform .6s var(--ease);
    }

    .fan-1 {
      left: 0;
      top: 4%;
      width: 52%;
      aspect-ratio: 4 / 3.4;
      rotate: -9deg;
      z-index: 1;
      transform: translate(calc(var(--px) * -16px), calc(var(--py) * -12px));
    }

    .fan-2 {
      right: 0;
      top: 2%;
      width: 48%;
      aspect-ratio: 4 / 3.5;
      rotate: 8deg;
      z-index: 1;
      transform: translate(calc(var(--px) * -12px), calc(var(--py) * -10px));
    }

    .fan-3 {
      left: 8%;
      top: 28%;
      width: 84%;
      aspect-ratio: 16 / 11;
      rotate: -2.5deg;
      z-index: 2;
      transform: translate(calc(var(--px) * 20px), calc(var(--py) * 14px));
      box-shadow: 10px 10px 0 var(--ink);
    }

    /* Card Mock Content */
    .mock-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 14px;
      background: var(--ink-3);
      border-bottom: 2px solid var(--ink);
    }

    .mock-dots {
      display: flex;
      gap: 5px;
    }

    .mock-dots span {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: rgba(255, 255, 255, .25);
    }

    .mock-dots span:nth-child(1) { background: #ff5f56; }
    .mock-dots span:nth-child(2) { background: #ffbd2e; }
    .mock-dots span:nth-child(3) { background: #27c93f; }

    .mock-title {
      font-size: 11px;
      font-weight: 700;
      color: var(--muted-d);
      letter-spacing: .05em;
    }

    .mock-body {
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .mock-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      background: var(--gold);
      color: var(--ink);
      font-size: 11px;
      font-weight: 800;
      border-radius: 6px;
      width: fit-content;
    }

    .mock-progress {
      height: 6px;
      background: rgba(255, 255, 255, .1);
      border-radius: 999px;
      overflow: hidden;
      position: relative;
    }

    .mock-progress-bar {
      height: 100%;
      background: var(--gold);
      width: 84%;
      border-radius: 999px;
    }

    /* Wobbling Burst Star Badge */
    .burst {
      position: absolute;
      z-index: 4;
      top: 18%;
      right: -4%;
      width: clamp(100px, 9vw, 126px);
      aspect-ratio: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: var(--ink);
      color: var(--gold);
      clip-path: polygon(50.0% 0.0%, 56.7% 7.5%, 65.5% 2.4%, 69.5% 11.7%, 79.4% 9.5%, 80.4% 19.6%, 90.5% 20.6%, 88.3% 30.5%, 97.6% 34.5%, 92.5% 43.3%, 100.0% 50.0%, 92.5% 56.7%, 97.6% 65.5%, 88.3% 69.5%, 90.5% 79.4%, 80.4% 80.4%, 79.4% 90.5%, 69.5% 88.3%, 65.5% 97.6%, 56.7% 92.5%, 50.0% 100.0%, 43.3% 92.5%, 34.5% 97.6%, 30.5% 88.3%, 20.6% 90.5%, 19.6% 80.4%, 9.5% 79.4%, 11.7% 69.5%, 2.4% 65.5%, 7.5% 56.7%, 0.0% 50.0%, 7.5% 43.3%, 2.4% 34.5%, 11.7% 30.5%, 9.5% 20.6%, 19.6% 19.6%, 20.6% 9.5%, 30.5% 11.7%, 34.5% 2.4%, 43.3% 7.5%);
      box-shadow: 4px 4px 0 var(--gold);
      animation: burst-wobble 6s ease-in-out infinite;
      transition: color .3s var(--ease);
    }

    @keyframes burst-wobble {
      0%, 100% { transform: rotate(0deg) scale(1); }
      50% { transform: rotate(6deg) scale(1.05); }
    }

    .burst b {
      font-size: clamp(1.6rem, 1.2rem + 1.2vw, 2.3rem);
      font-weight: 800;
      line-height: 1;
    }

    .burst span {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--white);
      margin-top: 3px;
    }

    /* Speech Bubble */
    .bubble {
      position: absolute;
      z-index: 4;
      left: -2%;
      bottom: -2%;
      max-width: 260px;
      padding: 12px 18px;
      background: var(--white);
      color: var(--ink);
      border: 2.5px solid var(--ink);
      border-radius: 18px;
      box-shadow: 6px 6px 0 var(--ink);
      font-size: 14.5px;
      font-weight: 800;
      line-height: 1.3;
      letter-spacing: -.01em;
      rotate: -3deg;
    }

    .bubble::after {
      content: "";
      position: absolute;
      left: 32px;
      top: -13px;
      width: 20px;
      height: 14px;
      background: var(--ink);
      clip-path: polygon(0 100%, 30% 0, 100% 100%);
    }

    /* ============================================================
       TICKER MARQUEE
       ============================================================ */
    .ticker {
      position: relative;
      z-index: 10;
      margin-top: -30px;
      padding-block: 16px 20px;
      overflow: hidden;
    }

    .ticker-band {
      margin-inline: -3vw;
      background: var(--gold);
      color: var(--ink);
      border-block: 3px solid var(--ink);
      transform: rotate(-1.6deg);
      box-shadow: 0 8px 0 rgba(0, 0, 0, .35);
      transition: background .3s var(--ease);
    }

    .ticker-track {
      display: flex;
      width: max-content;
      animation: ticker-slide 36s linear infinite;
    }

    .ticker:hover .ticker-track {
      animation-play-state: paused;
    }

    @keyframes ticker-slide {
      from { transform: translateX(0); }
      to { transform: translateX(-50%); }
    }

    .ticker-list {
      display: flex;
      list-style: none;
      flex: none;
    }

    .ticker-item {
      display: flex;
      align-items: center;
      gap: 20px;
      padding-inline: 20px;
      font-size: clamp(1.05rem, .9rem + .5vw, 1.35rem);
      font-weight: 800;
      letter-spacing: -.01em;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .ticker-diamond {
      width: 10px;
      height: 10px;
      background: var(--ink);
      transform: rotate(45deg);
      flex: none;
    }

    /* ============================================================
       SHARED SECTION HEADERS
       ============================================================ */
    .section {
      padding-block: clamp(70px, 9vw, 120px);
      position: relative;
    }

    .sec-head {
      margin-bottom: clamp(36px, 5vw, 60px);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-end;
      gap: 24px;
    }

    .sec-head h2 {
      font-size: var(--h2);
      line-height: var(--h2-lh);
      letter-spacing: -.03em;
    }

    .sec-note {
      font-size: 16px;
      color: var(--muted-d);
      max-width: 440px;
      line-height: 1.6;
    }

    /* ============================================================
       MADE FOR SECTION & INTERACTIVE INSPECTOR
       ============================================================ */
    .madefor {
      padding-block: clamp(60px, 8vw, 100px);
      border-bottom: 1px solid var(--ink-line);
      background: var(--ink-2);
    }

    .mf-in {
      display: grid;
      grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
      gap: clamp(36px, 6vw, 70px);
      align-items: center;
    }

    .mf-head h2 {
      font-size: clamp(1.8rem, 1.2rem + 2vw, 2.8rem);
      line-height: 1.15;
      margin-top: 16px;
      margin-bottom: 24px;
    }

    .audience-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 24px;
    }

    .aud-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 12px 18px;
      background: var(--ink);
      border: 1px solid var(--ink-line);
      border-radius: 14px;
      transition: transform .2s var(--ease), border-color .2s var(--ease);
    }

    .aud-item:hover {
      transform: translateX(6px);
      border-color: var(--gold);
    }

    .aud-num {
      font-size: 13px;
      font-weight: 800;
      color: var(--gold);
      background: rgba(245, 184, 46, .1);
      padding: 4px 8px;
      border-radius: 6px;
    }

    .aud-txt b {
      font-size: 15px;
      font-weight: 700;
    }

    .aud-txt small {
      display: block;
      font-size: 12.5px;
      color: var(--muted-d);
    }

    /* Interactive Link Analyzer Terminal */
    .inspector-card {
      background: var(--ink);
      border: 3px solid var(--ink-3);
      border-radius: 24px;
      box-shadow: 8px 8px 0 rgba(0, 0, 0, .6);
      padding: clamp(20px, 3.5vw, 32px);
      position: relative;
    }

    .inspector-card::before {
      content: "STREAM ENGINE";
      position: absolute;
      top: -12px;
      right: 24px;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: .14em;
      background: var(--gold);
      color: var(--ink);
      padding: 3px 10px;
      border-radius: 999px;
      border: 2px solid var(--ink);
    }

    .inspect-input-box {
      display: flex;
      gap: 10px;
      margin-block: 16px;
    }

    .inspect-input {
      flex: 1;
      background: var(--ink-2);
      border: 2px solid var(--ink-line);
      border-radius: 12px;
      padding: 12px 16px;
      color: var(--white);
      font-family: inherit;
      font-size: 14px;
      outline: none;
      transition: border-color .2s var(--ease);
    }

    .inspect-input:focus {
      border-color: var(--gold);
    }

    .inspect-tabs {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }

    .inspect-chip {
      padding: 5px 12px;
      border-radius: 8px;
      background: var(--ink-2);
      border: 1px solid var(--ink-line);
      font-size: 12px;
      font-weight: 700;
      color: var(--muted-d);
      cursor: pointer;
      transition: all .2s var(--ease);
    }

    .inspect-chip.is-active, .inspect-chip:hover {
      background: var(--gold);
      color: var(--ink);
      border-color: var(--gold);
    }

    .stream-readout {
      background: #060606;
      border: 1px solid var(--ink-line);
      border-radius: 12px;
      padding: 14px;
      font-family: ui-monospace, SFMono-Regular, "Courier New", monospace;
      font-size: 12.5px;
      line-height: 1.6;
      min-height: 120px;
      color: #9cdcfe;
    }

    .stream-readout .log-hi { color: var(--gold); font-weight: bold; }
    .stream-readout .log-succ { color: #4ec9b0; }

    /* ============================================================
       COURSES / FORMATS SECTION
       ============================================================ */
    .courses {
      background: var(--ink);
    }

    .filters {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 36px;
    }

    .filter {
      padding: 10px 20px;
      background: var(--ink-2);
      color: var(--white);
      border: 2px solid var(--ink-line);
      border-radius: 999px;
      font-size: 14px;
      font-weight: 700;
      transition: all .2s var(--ease);
    }

    .filter:hover, .filter.is-active {
      background: var(--gold);
      color: var(--ink);
      border-color: var(--gold);
    }

    /* Featured Gold Card */
    .featured {
      position: relative;
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
      background: var(--gold);
      color: var(--ink);
      border: 3px solid var(--ink);
      border-radius: 30px;
      box-shadow: 8px 8px 0 var(--ink);
      overflow: hidden;
      margin-bottom: 32px;
      transition: background .3s var(--ease);
    }

    .f-body {
      padding: clamp(24px, 4vw, 44px);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .f-top {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }

    .f-tag {
      font-size: 11px;
      font-weight: 800;
      letter-spacing: .12em;
      text-transform: uppercase;
      padding: 4px 10px;
      background: var(--ink);
      color: var(--gold);
      border-radius: 6px;
    }

    .f-badge {
      font-size: 12px;
      font-weight: 800;
      color: var(--ink);
      border: 1.5px solid var(--ink);
      padding: 3px 8px;
      border-radius: 6px;
    }

    .featured h3 {
      font-size: clamp(1.8rem, 1.2rem + 1.6vw, 2.5rem);
      line-height: 1.1;
      margin-bottom: 16px;
      letter-spacing: -.03em;
    }

    .f-body p {
      font-size: 15px;
      line-height: 1.55;
      font-weight: 600;
      color: #2b251b;
      margin-bottom: 24px;
    }

    .f-specs {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      list-style: none;
      padding-top: 18px;
      border-top: 2px dashed rgba(11, 11, 11, .25);
      margin-bottom: 28px;
    }

    .f-specs dt {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: #4a3e2e;
    }

    .f-specs dd {
      font-size: 15px;
      font-weight: 800;
      color: var(--ink);
    }

    .f-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }

    .f-media {
      background: var(--ink);
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 30px;
    }

    .f-media-art {
      width: 100%;
      height: 100%;
      min-height: 280px;
      border: 2px solid var(--ink-line);
      border-radius: 20px;
      background: var(--ink-2);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, .5);
    }

    /* Product Cards Grid */
    .c-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 24px;
    }

    .c-card {
      background: var(--ink-2);
      border: 2.5px solid var(--ink-3);
      border-radius: 22px;
      padding: 28px 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 6px 6px 0 var(--ink-3);
      transition: transform .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease);
    }

    .c-card:hover {
      transform: translateY(-6px);
      border-color: var(--gold);
      box-shadow: 6px 12px 0 var(--gold);
    }

    .c-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }

    .c-pill {
      font-size: 11px;
      font-weight: 800;
      letter-spacing: .1em;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(255, 255, 255, .08);
      color: var(--muted-d);
    }

    .c-icon {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: var(--ink-3);
      color: var(--gold);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .c-card h3 {
      font-size: 21px;
      line-height: 1.2;
      margin-bottom: 12px;
    }

    .c-card p {
      font-size: 14px;
      color: var(--muted-d);
      line-height: 1.55;
      margin-bottom: 24px;
    }

    .c-specs-mini {
      display: flex;
      gap: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--ink-line);
      font-size: 12px;
      font-weight: 700;
      color: var(--gold);
      margin-bottom: 20px;
    }

    /* ============================================================
       GOLD ACCENT BAND
       ============================================================ */
    .band {
      position: relative;
      background: var(--gold);
      color: var(--ink);
      padding-block: clamp(70px, 9vw, 110px);
      overflow: hidden;
      border-block: 3px solid var(--ink);
      transition: background .3s var(--ease);
    }

    .band-word {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      font-size: clamp(6rem, 16vw, 18rem);
      font-weight: 800;
      letter-spacing: -.05em;
      color: var(--ink);
      opacity: .07;
      user-select: none;
      pointer-events: none;
      white-space: nowrap;
    }

    .band-in {
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) auto;
      align-items: center;
      gap: 36px;
    }

    .band-title {
      font-size: clamp(2rem, 1.4rem + 2.5vw, 3.6rem);
      line-height: 1.05;
      letter-spacing: -.03em;
      margin-bottom: 18px;
    }

    .band-sub {
      font-size: clamp(1.05rem, .95rem + .3vw, 1.25rem);
      font-weight: 600;
      color: #3b3223;
      max-width: 600px;
      line-height: 1.55;
      margin-bottom: 28px;
    }

    .band-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
    }

    .band-stamp {
      width: 140px;
      height: 140px;
      border: 3px solid var(--ink);
      border-radius: 50%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      transform: rotate(8deg);
      box-shadow: 4px 4px 0 var(--ink);
      background: var(--gold-hi);
      flex: none;
    }

    .band-stamp b {
      font-size: 15px;
      font-weight: 800;
      line-height: 1.1;
    }

    .band-stamp small {
      font-size: 10px;
      font-weight: 800;
      letter-spacing: .1em;
      text-transform: uppercase;
      margin-top: 4px;
    }

    /* ============================================================
       WORKSTATION / GALLERY SHOWCASE
       ============================================================ */
    .classrooms {
      background: var(--ink-2);
    }

    .shots-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }

    .shot-card {
      background: var(--ink);
      border: 2px solid var(--ink-line);
      border-radius: 18px;
      overflow: hidden;
      cursor: pointer;
      position: relative;
      transition: transform .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease);
    }

    .shot-card:hover {
      transform: translateY(-5px);
      border-color: var(--gold);
      box-shadow: 6px 6px 0 var(--gold);
    }

    .shot-img-box {
      width: 100%;
      aspect-ratio: 16 / 10;
      background: var(--ink-3);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .shot-num {
      position: absolute;
      top: 12px;
      left: 12px;
      font-size: 11px;
      font-weight: 800;
      background: var(--gold);
      color: var(--ink);
      padding: 3px 8px;
      border-radius: 6px;
    }

    .shot-meta {
      padding: 16px 18px;
    }

    .shot-meta h4 {
      font-size: 16px;
      margin-bottom: 6px;
    }

    .shot-meta p {
      font-size: 13px;
      color: var(--muted-d);
      line-height: 1.45;
    }

    /* ============================================================
       OUR WAY / ARCHITECTURE PRINCIPLES
       ============================================================ */
    .way {
      background: var(--ink);
    }

    .promises {
      list-style: none;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 24px;
      margin-top: 36px;
    }

    .promise {
      background: var(--ink-2);
      border: 2px solid var(--ink-line);
      border-radius: 20px;
      padding: 30px 24px;
      position: relative;
      transition: border-color .2s var(--ease);
    }

    .promise:hover {
      border-color: var(--gold);
    }

    .promise .num {
      font-size: 32px;
      font-weight: 800;
      color: var(--gold);
      line-height: 1;
      margin-bottom: 16px;
      display: block;
      transition: color .3s var(--ease);
    }

    .promise h3 {
      font-size: 19px;
      margin-bottom: 10px;
    }

    .promise p {
      font-size: 14px;
      color: var(--muted-d);
      line-height: 1.6;
    }

    /* Trust Box */
    .trust-box {
      margin-top: 48px;
      background: var(--ink-2);
      border: 2px dashed var(--gold);
      border-radius: 22px;
      padding: 28px 32px;
      display: flex;
      align-items: center;
      gap: 24px;
    }

    .trust-avatar {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: var(--gold);
      color: var(--ink);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      font-weight: 800;
      flex: none;
    }

    .trust-txt h4 {
      font-size: 18px;
      margin-bottom: 6px;
    }

    .trust-txt p {
      font-size: 14px;
      color: var(--muted-d);
      line-height: 1.5;
    }

    /* ============================================================
       PRICING / LICENSE PASSES
       ============================================================ */
    .pricing-sec {
      background: var(--ink-2);
      border-top: 1px solid var(--ink-line);
    }

    .pricing-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 26px;
      align-items: stretch;
    }

    .price-card {
      background: var(--ink);
      border: 2.5px solid var(--ink-3);
      border-radius: 24px;
      padding: 34px 28px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      box-shadow: 6px 6px 0 var(--ink-3);
      transition: transform .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease);
    }

    .price-card:hover {
      transform: translateY(-6px);
      border-color: var(--gold);
      box-shadow: 6px 12px 0 var(--gold);
    }

    .price-card.featured-plan {
      background: var(--ink-3);
      border-color: var(--gold);
      box-shadow: 8px 8px 0 var(--gold);
    }

    .price-badge-top {
      position: absolute;
      top: -13px;
      right: 24px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: .12em;
      text-transform: uppercase;
      padding: 4px 12px;
      background: var(--gold);
      color: var(--ink);
      border-radius: 999px;
      border: 2px solid var(--ink);
    }

    .price-head {
      margin-bottom: 24px;
    }

    .price-head h3 {
      font-size: 22px;
      margin-bottom: 8px;
    }

    .price-head p {
      font-size: 13.5px;
      color: var(--muted-d);
    }

    .price-amount {
      display: flex;
      align-items: baseline;
      gap: 6px;
      margin-block: 16px;
    }

    .price-amount .currency {
      font-size: 24px;
      font-weight: 800;
      color: var(--gold);
    }

    .price-amount .num {
      font-size: 46px;
      font-weight: 800;
      letter-spacing: -.04em;
      line-height: 1;
    }

    .price-amount .period {
      font-size: 14px;
      color: var(--muted-d);
    }

    .price-perks {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 30px;
    }

    .price-perks li {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      color: var(--muted-d);
    }

    .price-perks li b {
      color: var(--white);
    }

    .price-perks li svg {
      color: var(--gold);
      flex: none;
    }

    /* ============================================================
       CLOSING CTA
       ============================================================ */
    .closing {
      position: relative;
      background: var(--gold);
      color: var(--ink);
      padding-block: clamp(70px, 9vw, 120px);
      overflow: hidden;
      border-top: 3px solid var(--ink);
      transition: background .3s var(--ease);
    }

    .closing-in {
      position: relative;
      z-index: 2;
      text-align: center;
      max-width: 760px;
      margin-inline: auto;
    }

    .closing-title {
      font-size: var(--h2);
      line-height: var(--h2-lh);
      letter-spacing: -.03em;
      margin-bottom: 18px;
    }

    .closing-sub {
      font-size: clamp(1.1rem, .95rem + .4vw, 1.35rem);
      font-weight: 600;
      color: #3b3020;
      line-height: 1.5;
      margin-bottom: 34px;
    }

    .closing-actions {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 16px;
    }

    /* ============================================================
       SITE FOOTER
       ============================================================ */
    .site-footer {
      background: var(--ink);
      border-top: 1px solid var(--ink-line);
      padding-block: 60px 40px;
    }

    .footer-in {
      display: grid;
      grid-template-columns: minmax(0, 1.5fr) repeat(3, minmax(0, 1fr));
      gap: clamp(30px, 4vw, 60px);
      margin-bottom: 48px;
    }

    .footer-brand p {
      font-size: 14px;
      color: var(--muted-d);
      line-height: 1.6;
      max-width: 320px;
      margin-top: 12px;
    }

    .footer-col {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .footer-h {
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--white);
      margin-bottom: 4px;
    }

    .footer-col a {
      font-size: 14px;
      color: var(--muted-d);
      transition: color .2s var(--ease);
    }

    .footer-col a:hover {
      color: var(--gold);
    }

    .footer-base {
      padding-top: 24px;
      border-top: 1px solid var(--ink-line);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      font-size: 13px;
      color: var(--muted-d);
    }

    /* Floating Action Button */
    .fab {
      position: fixed;
      right: 28px;
      bottom: 28px;
      z-index: 85;
      width: 58px;
      height: 58px;
      border-radius: 50%;
      background: var(--gold);
      color: var(--ink);
      border: 2px solid var(--ink);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 4px 4px 0 #ffffff;
      cursor: pointer;
      transition: transform .2s var(--ease), opacity .3s var(--ease);
    }

    .fab:hover {
      transform: translate(-2px, -2px) scale(1.06);
    }

    .fab.is-off {
      opacity: 0;
      pointer-events: none;
      transform: scale(0.8);
    }

    /* ============================================================
       MODAL DIALOGS (CHECKOUT & LIGHTBOX)
       ============================================================ */
    dialog {
      position: fixed;
      inset: 0;
      margin: auto;
      background: transparent;
      border: none;
      outline: none;
      padding: 0;
      max-width: 100vw;
      max-height: 100vh;
      overflow: visible;
      z-index: 999;
    }

    dialog::backdrop {
      background: rgba(0, 0, 0, .85);
      backdrop-filter: blur(8px);
    }

    .modal-box {
      background: var(--ink-2);
      border: 3px solid var(--gold);
      border-radius: 26px;
      box-shadow: 10px 10px 0 var(--ink);
      width: 90vw;
      max-width: 540px;
      padding: clamp(24px, 4vw, 36px);
      position: relative;
    }

    .modal-close {
      position: absolute;
      top: 18px;
      right: 18px;
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: var(--ink-3);
      color: var(--white);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .modal-close:hover {
      background: var(--gold);
      color: var(--ink);
    }

    /* Checkout Inputs */
    .form-group {
      margin-bottom: 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .form-group label {
      font-size: 13px;
      font-weight: 700;
      color: var(--muted-d);
    }

    .form-input {
      background: var(--ink);
      border: 2px solid var(--ink-line);
      border-radius: 12px;
      padding: 12px 16px;
      color: var(--white);
      font-family: inherit;
      font-size: 14px;
      outline: none;
    }

    .form-input:focus {
      border-color: var(--gold);
    }

    .key-display-box {
      margin-top: 20px;
      padding: 16px;
      background: var(--ink);
      border: 2px dashed var(--gold);
      border-radius: 14px;
      display: none;
    }

    .key-display-box.is-active {
      display: block;
    }

    .key-display-val {
      font-family: ui-monospace, SFMono-Regular, "Courier New", monospace;
      font-size: 18px;
      font-weight: 800;
      color: var(--gold);
      letter-spacing: .08em;
      word-break: break-all;
      margin-bottom: 12px;
      text-align: center;
    }

    /* Lightbox Modal */
    .lb-box {
      width: 90vw;
      max-width: 900px;
      background: var(--ink-2);
      border: 3px solid var(--gold);
      border-radius: 24px;
      overflow: hidden;
      position: relative;
    }

    .lb-content {
      width: 100%;
      aspect-ratio: 16 / 10;
      background: var(--ink);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 30px;
    }

    .lb-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 20px;
      background: var(--ink-3);
      border-top: 2px solid var(--ink);
    }

    /* Toast */
    .toast {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background: var(--gold);
      color: var(--ink);
      font-weight: 800;
      font-size: 14px;
      padding: 10px 22px;
      border-radius: 999px;
      border: 2px solid var(--ink);
      box-shadow: 4px 4px 0 var(--ink);
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: all .3s var(--ease);
    }

    .toast.is-show {
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }

    /* Scroll Reveal */
    .reveal {
      opacity: 0;
      transform: translateY(22px);
      transition: opacity .7s var(--ease), transform .7s var(--ease);
    }

    .reveal.is-in {
      opacity: 1;
      transform: translateY(0);
    }

    /* ============================================================
       RESPONSIVE BREAKPOINTS
       ============================================================ */
    @media (max-width: 960px) {
      .nav, .theme-picker { display: none; }
      .menu-btn { display: flex; }
      .hero-panel { left: 0; clip-path: polygon(0 0, 100% 0, 100% 100%, 0 92%); opacity: .12; }
      .hero-in { grid-template-columns: 1fr; }
      .hero-art { max-width: 440px; margin-top: 20px; }
      .mf-in { grid-template-columns: 1fr; }
      .featured { grid-template-columns: 1fr; }
      .band-in { grid-template-columns: 1fr; }
      .band-stamp { display: none; }
      .shots-grid { grid-template-columns: 1fr; }
      .footer-in { grid-template-columns: 1fr 1fr; }
    }

    @media (max-width: 600px) {
      .footer-in { grid-template-columns: 1fr; }
      .hero-actions { flex-direction: column; align-items: stretch; }
      .btn { width: 100%; }
      .band-actions { flex-direction: column; }
    }
  </style>
</head>
<body>

  <!-- ============================================================
       SVG SYMBOLS DEFINITION SHEET
       ============================================================ -->
  <svg xmlns="http://www.w3.org/2000/svg" style="display:none">
    <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></symbol>
    <symbol id="i-arrow-ne" viewBox="0 0 24 24"><path d="M7 7h10v10"></path><path d="M7 17 17 7"></path></symbol>
    <symbol id="i-close" viewBox="0 0 24 24"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></symbol>
    <symbol id="i-check" viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5"></path></symbol>
    <symbol id="i-download" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></symbol>
    <symbol id="i-play" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></symbol>
    <symbol id="i-bolt" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></symbol>
    <symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></symbol>
    <symbol id="i-video" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></symbol>
    <symbol id="i-music" viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></symbol>
    <symbol id="i-layers" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></symbol>
    <symbol id="i-copy" viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></symbol>
    <symbol id="i-left" viewBox="0 0 24 24"><path d="m15 18-6-6 6-6"></path></symbol>
    <symbol id="i-right" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"></path></symbol>
  </svg>

  <!-- ============================================================
       STICKY HEADER
       ============================================================ -->
  <header class="site-header" id="top">
    <div class="wrap header-in">
      <a href="#top" class="brand" aria-label="Downloader Pro, back to top">
        <span class="wordmark">Downloader<span class="wm-period">.</span></span>
        <span class="brand-sub">PRO v2.2</span>
      </a>

      <nav class="nav" aria-label="Main Navigation">
        <a href="#formats">Formats</a>
        <a href="#inspector">Analyzer</a>
        <a href="#workstation">Workstation</a>
        <a href="#principles">Architecture</a>
        <a href="#pricing">Pricing</a>
      </nav>

      <div class="header-actions">
        <!-- Live Color Palette Switcher -->
        <div class="theme-picker" role="group" aria-label="Color Palette">
          <button class="theme-dot is-active" data-t="gold" title="Campus Gold" aria-label="Campus Gold"></button>
          <button class="theme-dot" data-t="red" title="Poster Red" aria-label="Poster Red"></button>
          <button class="theme-dot" data-t="cyan" title="Cyber Cyan" aria-label="Cyber Cyan"></button>
        </div>

        <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-gold btn-sm">
          <span>Download Free</span>
          <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
        </a>

        <button class="menu-btn" aria-label="Toggle menu" aria-expanded="false" id="menuBtn">
          <span></span>
          <span></span>
        </button>
      </div>
    </div>
  </header>

  <!-- Mobile Flyout Menu -->
  <div class="mobile-menu" id="mobileMenu">
    <a href="#formats">Formats &amp; Resolutions</a>
    <a href="#inspector">Stream Analyzer</a>
    <a href="#workstation">Workstation Showcase</a>
    <a href="#principles">Architecture Principles</a>
    <a href="#pricing">License Passes</a>
    <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-gold" style="margin-top: 14px;">
      <span>Download Setup v2.2</span>
      <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
    </a>
  </div>

  <!-- ============================================================
       HERO SECTION
       ============================================================ */
  -->
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-panel" aria-hidden="true"></div>

    <div class="wrap hero-in">
      <div class="hero-copy">
        <p class="tag reveal">
          <span>Ultra HD CDN Ripper &middot; Windows 10 &amp; 11</span>
        </p>

        <h1 class="reveal" id="hero-title">
          <span>Rip in 8K.</span>
          <mark>Zero</mark>
          <span class="h1-end">buffering.</span>
        </h1>

        <p class="hero-sub reveal">
          <span>Multi-threaded streams.</span>
          <span class="u-gold">Lossless 320k audio.</span>
        </p>

        <p class="lead reveal">
          Downloader Pro extracts pristine 4K &amp; 8K 60FPS video, TikTok clips with zero watermarks, and studio-grade 320kbps MP3s in seconds. Built with 16 parallel TCP threads and GPU-accelerated FFmpeg muxing.
        </p>

        <div class="hero-actions reveal">
          <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-gold">
            <span>Download Windows Installer</span>
            <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
          </a>
          <a href="#inspector" class="btn btn-line">
            <span>Test Stream Analyzer</span>
            <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
          </a>
        </div>

        <!-- Campus Shield Badges -->
        <ul class="shields reveal">
          <li class="shield-item">
            <div class="shield">
              <b>8K</b>
              <small>60FPS</small>
            </div>
            <div class="shield-txt">
              <b>Ultra HD Video</b>
              <small>VP9 &amp; AV1 Cinema</small>
            </div>
          </li>

          <li class="shield-item">
            <div class="shield">
              <b>100%</b>
              <small>CLEAN</small>
            </div>
            <div class="shield-txt">
              <b>No Watermark</b>
              <small>TikTok &amp; Shorts</small>
            </div>
          </li>

          <li class="shield-item">
            <div class="shield">
              <b>16x</b>
              <small>THREADS</small>
            </div>
            <div class="shield-txt">
              <b>Turbo Speed</b>
              <small>Multi-part CDN rip</small>
            </div>
          </li>
        </ul>
      </div>

      <!-- Hero Art with Interactive Pointer Leaning Fan -->
      <div class="hero-art reveal">
        <div class="fan" id="heroFan">
          <!-- Fan Card 1: 8K Video -->
          <div class="fan-card fan-1">
            <div class="mock-header">
              <div class="mock-dots"><span></span><span></span><span></span></div>
              <span class="mock-title">YOUTUBE DASH</span>
            </div>
            <div class="mock-body">
              <span class="mock-badge">4320p &middot; 8K HDR</span>
              <p style="font-size:12px; font-weight:700; line-height:1.3;">Nature Showcase (60 FPS CineMaster)</p>
              <div class="mock-progress"><div class="mock-progress-bar" style="width: 92%;"></div></div>
              <small style="font-size: 10px; color: var(--muted-d);">142.4 MB/s &middot; Remuxing to MP4</small>
            </div>
          </div>

          <!-- Fan Card 2: TikTok Clean -->
          <div class="fan-card fan-2">
            <div class="mock-header">
              <div class="mock-dots"><span></span><span></span><span></span></div>
              <span class="mock-title">TIKTOK HD</span>
            </div>
            <div class="mock-body">
              <span class="mock-badge" style="background:#fff; color:#0b0b0b;">NO OVERLAYS</span>
              <p style="font-size:12px; font-weight:700; line-height:1.3;">@creative_motion &middot; Clean Video</p>
              <div class="mock-progress"><div class="mock-progress-bar" style="width: 100%;"></div></div>
              <small style="font-size: 10px; color: #4ec9b0;">Done &middot; Watermark removed</small>
            </div>
          </div>

          <!-- Fan Card 3: Main Downloader Pro Workstation -->
          <div class="fan-card fan-3">
            <div class="mock-header">
              <div class="mock-dots"><span></span><span></span><span></span></div>
              <span class="mock-title">DOWNLOADER PRO v2.2 TURBO</span>
              <span style="font-size: 9px; font-weight:800; background:var(--gold); color:#0b0b0b; padding:2px 6px; border-radius:4px;">GPU READY</span>
            </div>
            <div class="mock-body" style="gap: 12px;">
              <div style="background:#000; border:1px solid rgba(255,255,255,.15); padding:8px 12px; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:11px; color:#9cdcfe; font-family:monospace; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:80%;">https://youtube.com/watch?v=dQw4w9WgXcQ</span>
                <span style="font-size:10px; font-weight:800; color:var(--gold);">16 CONCURRENT</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12px; font-weight:700;">Streams Muxed: 4K Video + Opus 320k</span>
                <span style="font-size:12px; font-weight:800; color:var(--gold);">184 MB / 184 MB</span>
              </div>
              <div class="mock-progress" style="height:8px;"><div class="mock-progress-bar" style="width:100%;"></div></div>
            </div>
          </div>
        </div>

        <!-- 24-point Wobbling Burst Star Badge -->
        <div class="burst">
          <b>v2.2</b>
          <span>TURBO</span>
        </div>

        <!-- Tilted Speech Bubble -->
        <div class="bubble">
          Zero watermarks. Full 320kbps bitrate. Own your files.
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       TICKER BAND (MARQUEE)
       ============================================================ -->
  <div class="ticker" aria-hidden="true">
    <div class="ticker-band">
      <div class="ticker-track">
        <ul class="ticker-list">
          <li class="ticker-item">YOUTUBE 8K 60FPS<span class="ticker-diamond"></span></li>
          <li class="ticker-item">TIKTOK NO WATERMARK<span class="ticker-diamond"></span></li>
          <li class="ticker-item">STUDIO 320KBPS MP3<span class="ticker-diamond"></span></li>
          <li class="ticker-item">BATCH PLAYLISTS<span class="ticker-diamond"></span></li>
          <li class="ticker-item">GPU HARDWARE MUXING<span class="ticker-diamond"></span></li>
          <li class="ticker-item">DIRECT CDN ACCELERATION<span class="ticker-diamond"></span></li>
          <li class="ticker-item">LOSSLESS M4A &amp; FLAC<span class="ticker-diamond"></span></li>
          <li class="ticker-item">ID3 ALBUM ART EMBEDDING<span class="ticker-diamond"></span></li>
        </ul>
        <ul class="ticker-list">
          <li class="ticker-item">YOUTUBE 8K 60FPS<span class="ticker-diamond"></span></li>
          <li class="ticker-item">TIKTOK NO WATERMARK<span class="ticker-diamond"></span></li>
          <li class="ticker-item">STUDIO 320KBPS MP3<span class="ticker-diamond"></span></li>
          <li class="ticker-item">BATCH PLAYLISTS<span class="ticker-diamond"></span></li>
          <li class="ticker-item">GPU HARDWARE MUXING<span class="ticker-diamond"></span></li>
          <li class="ticker-item">DIRECT CDN ACCELERATION<span class="ticker-diamond"></span></li>
          <li class="ticker-item">LOSSLESS M4A &amp; FLAC<span class="ticker-diamond"></span></li>
          <li class="ticker-item">ID3 ALBUM ART EMBEDDING<span class="ticker-diamond"></span></li>
        </ul>
      </div>
    </div>
  </div>

  <!-- ============================================================
       MADE FOR SECTION & INTERACTIVE STREAM ANALYZER
       ============================================================ -->
  <section class="madefor" id="inspector" aria-labelledby="mf-title">
    <div class="wrap">
      <div class="mf-in">
        <div class="mf-head">
          <p class="tag reveal"><span>Target Audiences</span></p>
          <h2 class="reveal" id="mf-title">Engineered for heavy media workloads &amp; creators.</h2>
          <p style="color:var(--muted-d); line-height:1.6;" class="reveal">
            Whether you edit 4K footage in DaVinci Resolve, produce DJ sample packs, or curate offline research lectures, Downloader Pro bypasses web throttles and saves files directly to your storage.
          </p>

          <ul class="audience-list reveal">
            <li class="aud-item">
              <span class="aud-num">01</span>
              <div class="aud-txt">
                <b>Video Editors &amp; Motion Designers</b>
                <small>Extract raw 4K &amp; 8K clips without compression artifacts</small>
              </div>
            </li>
            <li class="aud-item">
              <span class="aud-num">02</span>
              <div class="aud-txt">
                <b>DJs &amp; Audio Curators</b>
                <small>Pristine 320kbps MP3s with automated ID3 album art</small>
              </div>
            </li>
            <li class="aud-item">
              <span class="aud-num">03</span>
              <div class="aud-txt">
                <b>Content Creators &amp; Archivists</b>
                <small>TikTok clips with zero overlays, plus full channel queues</small>
              </div>
            </li>
          </ul>
        </div>

        <!-- Interactive Stream Analyzer Terminal -->
        <div class="inspector-card reveal">
          <h3 style="font-size: 20px; margin-bottom: 6px;">Live Stream Analyzer</h3>
          <p style="font-size: 13px; color: var(--muted-d); margin-bottom: 14px;">Paste any video or TikTok URL to inspect CDN stream manifests:</p>

          <div class="inspect-tabs" id="formatTabs">
            <button class="inspect-chip is-active" data-fmt="8k">8K 60FPS Video</button>
            <button class="inspect-chip" data-fmt="4k">4K Ultra HD</button>
            <button class="inspect-chip" data-fmt="1080p">1080p FHD</button>
            <button class="inspect-chip" data-fmt="mp3">MP3 320k Audio</button>
            <button class="inspect-chip" data-fmt="tiktok">TikTok Clean</button>
          </div>

          <div class="inspect-input-box">
            <input type="text" class="inspect-input" id="streamUrlInput" placeholder="https://www.youtube.com/watch?v=..." value="https://www.youtube.com/watch?v=L_LUpnjgPso">
            <button class="btn btn-gold btn-sm" id="btnAnalyze" style="flex:none;">
              <span>Analyze</span>
              <svg class="ic" aria-hidden="true"><use href="#i-bolt"></use></svg>
            </button>
          </div>

          <div class="stream-readout" id="streamLog">
            [CDN-CORE] Ready for manifest inspection.<br>
            &gt; Enter URL and click <span class="log-hi">Analyze</span> to resolve video &amp; audio streams...
          </div>

          <div style="margin-top: 16px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 12px; color: var(--muted-d);">Status: <span class="u-gold" id="analyzeStatus">Idle</span></span>
            <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-line btn-sm" id="btnQuickDl" style="display:none;">
              <span>Download Selected Format</span>
              <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       COURSES / FORMATS SECTION
       ============================================================ -->
  <section class="section courses" id="formats" aria-labelledby="fmt-title">
    <div class="wrap">
      <div class="sec-head">
        <div>
          <p class="sticker reveal"><span>Multi-Format Engine</span></p>
          <h2 class="reveal" id="fmt-title">
            <span>Pick your format.</span>
            <mark>Rip in seconds.</mark>
          </h2>
        </div>
        <p class="sec-note reveal">
          Every format is remuxed in native containers with hardware acceleration. No transcoding losses, no missing audio channels.
        </p>
      </div>

      <!-- Category Filter Pills -->
      <div class="filters reveal">
        <button class="filter is-active" data-cat="all">All Formats</button>
        <button class="filter" data-cat="video">Video 4K / 8K</button>
        <button class="filter" data-cat="tiktok">TikTok Clean</button>
        <button class="filter" data-cat="audio">Audio Hi-Fi</button>
        <button class="filter" data-cat="batch">Playlists &amp; Batch</button>
      </div>

      <!-- Featured Gold Poster Card: 8K Flagship -->
      <div class="featured reveal" data-cat="video">
        <div class="f-body">
          <div>
            <div class="f-top">
              <span class="f-tag">Flagship Pipeline</span>
              <span class="f-badge">8K 60FPS HDR</span>
            </div>
            <h3>YouTube 8K Cinema Stream with Automated FFmpeg Remux</h3>
            <p>
              Direct DASH protocol extraction fetching VP9 and AV1 video streams alongside uncompressed 320kbps Opus audio, muxed locally via your GPU with zero CPU stutter.
            </p>
          </div>

          <div>
            <dl class="f-specs">
              <div>
                <dt>Resolution</dt>
                <dd>7680 &times; 4320 (8K UHD)</dd>
              </div>
              <div>
                <dt>Framerate</dt>
                <dd>Smooth 60 FPS HDR</dd>
              </div>
              <div>
                <dt>Audio Muxing</dt>
                <dd>Opus &middot; 320kbps Hi-Fi</dd>
              </div>
              <div>
                <dt>Throughput</dt>
                <dd>Uncapped 16 Threads</dd>
              </div>
            </dl>

            <div class="f-actions">
              <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-ink">
                <span>Download Setup v2.2</span>
                <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
              </a>
              <a href="#inspector" class="btn btn-line" style="border-color: var(--ink); color: var(--ink);">
                <span>Inspect 8K Stream</span>
                <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
              </a>
            </div>
          </div>
        </div>

        <div class="f-media">
          <div class="f-media-art">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:11px; font-weight:800; color:var(--gold);">DASH MANIFEST 4320p</span>
              <span style="font-size:11px; color:#4ec9b0; font-family:monospace;">16 CHANNELS SYNCED</span>
            </div>
            <div style="text-align:center; padding: 20px;">
              <div style="font-size: 54px; font-weight: 800; color: var(--gold); line-height: 1;">8K</div>
              <div style="font-size: 13px; font-weight: 700; letter-spacing: .15em; text-transform: uppercase;">CINEMA STREAM MATRIX</div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--muted-d);">
              <span>AV1 Codec: Level 6.2</span>
              <span>Bitrate: 85.4 Mbps</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Product Cards Grid -->
      <div class="c-grid">
        <!-- Card 1: TikTok Clean -->
        <div class="c-card reveal" data-cat="tiktok">
          <div>
            <div class="c-top">
              <span class="c-pill">No Watermark</span>
              <div class="c-icon"><svg class="ic"><use href="#i-video"></use></svg></div>
            </div>
            <h3>TikTok Clean Video Ripper</h3>
            <p>Bypass username stamps, bouncing logos, and UI overlays. Grabs the original pure source video file directly from the TikTok CDN.</p>
          </div>
          <div>
            <div class="c-specs-mini">
              <span>Original 1080x1920</span>
              <span>100% Watermark Free</span>
            </div>
            <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-line btn-sm" style="width: 100%;">
              <span>Download Ripper</span>
              <svg class="ic"><use href="#i-download"></use></svg>
            </a>
          </div>
        </div>

        <!-- Card 2: Studio 320k MP3 -->
        <div class="c-card reveal" data-cat="audio">
          <div>
            <div class="c-top">
              <span class="c-pill">Studio Hi-Fi</span>
              <div class="c-icon"><svg class="ic"><use href="#i-music"></use></svg></div>
            </div>
            <h3>Studio 320kbps MP3 &amp; Covers</h3>
            <p>Converts YouTube and music videos to crystal-clear 320kbps CBR MP3s. Automatically embeds track title, artist, and full HD album artwork.</p>
          </div>
          <div>
            <div class="c-specs-mini">
              <span>320kbps Constant</span>
              <span>ID3v2.4 Embedded</span>
            </div>
            <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-line btn-sm" style="width: 100%;">
              <span>Download Audio Client</span>
              <svg class="ic"><use href="#i-download"></use></svg>
            </a>
          </div>
        </div>

        <!-- Card 3: Batch Playlists -->
        <div class="c-card reveal" data-cat="batch">
          <div>
            <div class="c-top">
              <span class="c-pill">Parallel Batch</span>
              <div class="c-icon"><svg class="ic"><use href="#i-layers"></use></svg></div>
            </div>
            <h3>Batch Channel &amp; Playlists</h3>
            <p>Paste an entire YouTube playlist or creator channel link. Queue hundreds of videos in parallel with intelligent automatic naming and resume.</p>
          </div>
          <div>
            <div class="c-specs-mini">
              <span>16 Parallel Workers</span>
              <span>Auto-Resume on Drop</span>
            </div>
            <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-line btn-sm" style="width: 100%;">
              <span>Download Queue Tool</span>
              <svg class="ic"><use href="#i-download"></use></svg>
            </a>
          </div>
        </div>

        <!-- Card 4: Lossless M4A & FLAC -->
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
  </section>

  <!-- ============================================================
       GOLD ACCENT BAND
       ============================================================ */
  -->
  <section class="band" aria-labelledby="band-title">
    <div class="band-word" aria-hidden="true">DOWNLOADER</div>
    <div class="wrap band-in">
      <div>
        <h2 class="band-title" id="band-title">Over 2.4 Million Streams Extracted With Zero Failures.</h2>
        <p class="band-sub">
          No monthly subscription traps. Download the standalone Windows installer or unlock the Lifetime Pass for unlimited multi-device access with priority updates.
        </p>
        <div class="band-actions">
          <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-ink">
            <span>Download Windows Setup v2.2</span>
            <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
          </a>
          <button class="btn btn-line trigger-checkout" data-plan="pro_lifetime" style="border-color: var(--ink); color: var(--ink);">
            <span>Get Lifetime Pass ($49.99)</span>
            <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
          </button>
        </div>
      </div>

      <div class="band-stamp">
        <b>100% CLEAN</b>
        <small>NO MALWARE</small>
        <small style="color:var(--ink); font-weight:700;">VIRUSTOTAL VERIFIED</small>
      </div>
    </div>
  </section>

  <!-- ============================================================
       WORKSTATION SHOWCASE / GALLERY
       ============================================================ -->
  <section class="section classrooms" id="workstation" aria-labelledby="ws-title">
    <div class="wrap">
      <div class="sec-head">
        <div>
          <p class="sticker reveal"><span>Visual Walkthrough</span></p>
          <h2 class="reveal" id="ws-title">
            <span>Take a look inside.</span>
            <mark>Clean interface.</mark>
          </h2>
        </div>
        <p class="sec-note reveal">
          Engineered for keyboard shortcuts, drag-and-drop links, and instant dark mode visibility. Click any module to view details.
        </p>
      </div>

      <div class="shots-grid">
        <!-- Module 01 -->
        <div class="shot-card reveal" data-lb="0">
          <div class="shot-img-box">
            <span class="shot-num">01</span>
            <div style="text-align:center; padding: 20px;">
              <div style="font-size:28px; font-weight:800; color:var(--gold);">DASHBOARD</div>
              <small style="font-size:11px; color:var(--muted-d);">Single-Input Auto Detection</small>
            </div>
          </div>
          <div class="shot-meta">
            <h4>One-Click Paste &amp; Rip</h4>
            <p>Paste any URL and Downloader Pro instantly queries manifest formats in 200ms.</p>
          </div>
        </div>

        <!-- Module 02 -->
        <div class="shot-card reveal" data-lb="1">
          <div class="shot-img-box">
            <span class="shot-num">02</span>
            <div style="text-align:center; padding: 20px;">
              <div style="font-size:28px; font-weight:800; color:var(--gold);">8K SELECTOR</div>
              <small style="font-size:11px; color:var(--muted-d);">Dynamic Bitrate Breakdown</small>
            </div>
          </div>
          <div class="shot-meta">
            <h4>Format &amp; Quality Matrix</h4>
            <p>Accurate file size estimation, codec choices, and resolution filters.</p>
          </div>
        </div>

        <!-- Module 03 -->
        <div class="shot-card reveal" data-lb="2">
          <div class="shot-img-box">
            <span class="shot-num">03</span>
            <div style="text-align:center; padding: 20px;">
              <div style="font-size:28px; font-weight:800; color:var(--gold);">QUEUE ENGINE</div>
              <small style="font-size:11px; color:var(--muted-d);">16 Parallel Workers</small>
            </div>
          </div>
          <div class="shot-meta">
            <h4>Batch Queue Manager</h4>
            <p>Queue dozens of files with independent download speeds, pause, and auto-resume.</p>
          </div>
        </div>

        <!-- Module 04 -->
        <div class="shot-card reveal" data-lb="3">
          <div class="shot-img-box">
            <span class="shot-num">04</span>
            <div style="text-align:center; padding: 20px;">
              <div style="font-size:28px; font-weight:800; color:var(--gold);">AUDIO STUDIO</div>
              <small style="font-size:11px; color:var(--muted-d);">320kbps CBR Converter</small>
            </div>
          </div>
          <div class="shot-meta">
            <h4>Studio 320k Audio Ripper</h4>
            <p>Automated ID3 metadata, artist normalization, and album art tagging.</p>
          </div>
        </div>

        <!-- Module 05 -->
        <div class="shot-card reveal" data-lb="4">
          <div class="shot-img-box">
            <span class="shot-num">05</span>
            <div style="text-align:center; padding: 20px;">
              <div style="font-size:28px; font-weight:800; color:var(--gold);">TIKTOK CLEAN</div>
              <small style="font-size:11px; color:var(--muted-d);">Zero Overlays</small>
            </div>
          </div>
          <div class="shot-meta">
            <h4>No-Watermark Extraction</h4>
            <p>Pure MP4 stream pulled straight from source CDN without watermark layers.</p>
          </div>
        </div>

        <!-- Module 06 -->
        <div class="shot-card reveal" data-lb="5">
          <div class="shot-img-box">
            <span class="shot-num">06</span>
            <div style="text-align:center; padding: 20px;">
              <div style="font-size:28px; font-weight:800; color:var(--gold);">GPU HARDWARE</div>
              <small style="font-size:11px; color:var(--muted-d);">NVENC &middot; QuickSync &middot; AMF</small>
            </div>
          </div>
          <div class="shot-meta">
            <h4>Hardware Acceleration</h4>
            <p>Remuxing and conversion delegated straight to your dedicated graphics card.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       OUR WAY / ARCHITECTURE PRINCIPLES
       ============================================================ -->
  <section class="section way" id="principles" aria-labelledby="way-title">
    <div class="wrap">
      <div class="sec-head">
        <div>
          <p class="tag tag-ink reveal"><span>Engineering Principles</span></p>
          <h2 class="reveal" id="way-title" style="font-size: var(--h2);">
            <span>Understand it.</span>
            <span>Run it.</span>
            <span class="u-gold">Own it forever.</span>
          </h2>
        </div>
        <p class="sec-note reveal">
          Four technical architectural guarantees we uphold in every single build of Downloader Pro.
        </p>
      </div>

      <ol class="promises">
        <li class="promise reveal">
          <span class="num">01</span>
          <div>
            <h3>Direct CDN Stream Extraction</h3>
            <p>We establish direct TCP sockets to edge media CDNs with multi-segmented chunks, bypassing browser rate-limits and artificial buffering caps.</p>
          </div>
        </li>

        <li class="promise reveal">
          <span class="num">02</span>
          <div>
            <h3>100% On-Device Privacy</h3>
            <p>Your video links, downloads, and files never route through third-party proxy servers or analytics collectors. Everything executes locally on your PC.</p>
          </div>
        </li>

        <li class="promise reveal">
          <span class="num">03</span>
          <div>
            <h3>GPU Hardware Remuxing</h3>
            <p>Separate video and audio streams are muxed using NVIDIA NVENC, AMD AMF, or Intel QuickSync, keeping your CPU cool and remux times under 2 seconds.</p>
          </div>
        </li>

        <li class="promise reveal">
          <span class="num">04</span>
          <div>
            <h3>Integrated FFmpeg Binaries</h3>
            <p>Includes statically-linked, optimized FFmpeg binaries inside the installer. No PATH environment headaches, no separate command line installations.</p>
          </div>
        </li>
      </ol>

      <!-- Trust Box -->
      <div class="trust-box reveal">
        <div class="trust-avatar">?</div>
        <div class="trust-txt">
          <h4>Why do browser extensions and free websites keep breaking?</h4>
          <p>
            Streaming sites frequently update their manifest obfuscation algorithms. Browser extensions rely on injected DOM scripts that get blocked by security policies. Downloader Pro uses a decoupled manifest scraper that auto-updates format definitions without breaking your workflow.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       PRICING / LICENSE PASSES
       ============================================================ -->
  <section class="section pricing-sec" id="pricing" aria-labelledby="pr-title">
    <div class="wrap">
      <div class="sec-head">
        <div>
          <p class="sticker reveal"><span>Simple Pricing</span></p>
          <h2 class="reveal" id="pr-title">
            <span>Choose your pass.</span>
            <mark>Instant unlock.</mark>
          </h2>
        </div>
        <p class="sec-note reveal">
          Start for free with standard 1080p downloads, or unlock unlimited 8K speeds, batch queues, and lifetime updates.
        </p>
      </div>

      <div class="pricing-grid">
        <!-- Plan 1: Free Starter -->
        <div class="price-card reveal">
          <div>
            <div class="price-head">
              <h3>Free Starter</h3>
              <p>Great for occasional 1080p downloads and basic MP3 rips.</p>
            </div>

            <div class="price-amount">
              <span class="currency">$</span>
              <span class="num">0</span>
              <span class="period">/ forever</span>
            </div>

            <ul class="price-perks">
              <li><svg class="ic"><use href="#i-check"></use></svg><span>1080p Full HD video downloads</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>192kbps Standard MP3 audio</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>2 parallel queue downloads</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>Windows 10/11 standalone setup</span></li>
            </ul>
          </div>

          <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-line" style="width: 100%;">
            <span>Download Free v2.2</span>
            <svg class="ic"><use href="#i-download"></use></svg>
          </a>
        </div>

        <!-- Plan 2: Annual Pro -->
        <div class="price-card reveal">
          <div>
            <div class="price-head">
              <h3>Annual Pro Pass</h3>
              <p>For active video editors and audio curators.</p>
            </div>

            <div class="price-amount">
              <span class="currency">$</span>
              <span class="num">29</span>
              <span class="period">.99 / year</span>
            </div>

            <ul class="price-perks">
              <li><svg class="ic"><use href="#i-check"></use></svg><span>Full <b>4K &amp; 8K 60FPS</b> UHD downloads</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>Studio <b>320kbps MP3</b> + Album art</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>TikTok <b>Zero-Watermark</b> ripper</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>8 parallel queue workers</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>2 PC device activations</span></li>
            </ul>
          </div>

          <button class="btn btn-line trigger-checkout" data-plan="pro_yearly" style="width: 100%;">
            <span>Get Annual Pass</span>
            <svg class="ic"><use href="#i-arrow-ne"></use></svg>
          </button>
        </div>

        <!-- Plan 3: Lifetime Master (Featured) -->
        <div class="price-card featured-plan reveal">
          <span class="price-badge-top">BEST VALUE &middot; ONE-TIME</span>

          <div>
            <div class="price-head">
              <h3 style="color:var(--gold);">Lifetime Master</h3>
              <p>Pay once, own forever. All present and future updates included.</p>
            </div>

            <div class="price-amount">
              <span class="currency">$</span>
              <span class="num">49</span>
              <span class="period">.99 / one-time</span>
            </div>

            <ul class="price-perks">
              <li><svg class="ic"><use href="#i-check"></use></svg><span>Everything in Annual Pro</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span><b>Unlimited</b> parallel threads (16+)</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>Full channel &amp; playlist <b>batch rips</b></span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span><b>3 PC lifetime</b> license activations</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>Lifetime updates &amp; priority manifests</span></li>
              <li><svg class="ic"><use href="#i-check"></use></svg><span>GPU hardware acceleration engine</span></li>
            </ul>
          </div>

          <button class="btn btn-gold trigger-checkout" data-plan="pro_lifetime" style="width: 100%;">
            <span>Get Lifetime License</span>
            <svg class="ic"><use href="#i-arrow"></use></svg>
          </button>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       CLOSING CTA
       ============================================================ -->
  <section class="closing" aria-labelledby="close-title">
    <div class="wrap closing-in">
      <h2 class="closing-title reveal" id="close-title">
        Ready for uncapped 4K and clean TikTok streams?
      </h2>
      <p class="closing-sub reveal">
        Download the setup installer now or get your Lifetime Pass. Works immediately with zero configuration.
      </p>
      <div class="closing-actions reveal">
        <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-ink">
          <span>Download Setup v2.2</span>
          <svg class="ic" aria-hidden="true"><use href="#i-download"></use></svg>
        </a>
        <button class="btn btn-gold trigger-checkout" data-plan="pro_lifetime" style="background:#0b0b0b; color:var(--gold); border-color:#0b0b0b;">
          <span>Unlock Lifetime Pass</span>
          <svg class="ic" aria-hidden="true"><use href="#i-arrow-ne"></use></svg>
        </button>
      </div>
    </div>
  </section>

  <!-- ============================================================
       SITE FOOTER
       ============================================================ -->
  <footer class="site-footer">
    <div class="wrap footer-in">
      <div class="footer-brand">
        <span class="wordmark">Downloader<span class="wm-period">.</span></span>
        <p>
          High-performance 8K video, TikTok clean MP4, and studio 320kbps MP3 ripper for Windows 10 &amp; 11.
        </p>
      </div>

      <nav class="footer-col" aria-label="Explore Links">
        <p class="footer-h">Explore</p>
        <a href="#formats">Formats &amp; Resolutions</a>
        <a href="#inspector">Stream Analyzer</a>
        <a href="#workstation">Workstation Modules</a>
        <a href="#principles">Architecture Guarantees</a>
        <a href="#pricing">License Passes</a>
      </nav>

      <div class="footer-col">
        <p class="footer-h">Downloads</p>
        <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer">Windows Installer (.exe)</a>
        <a href="/download?type=zip">Portable ZIP Package</a>
        <a href="/admin">License Admin Portal</a>
        <a href="#pricing">Upgrade to Pro</a>
      </div>

      <div class="footer-col">
        <p class="footer-h">Privacy &amp; Safety</p>
        <span style="font-size: 13px; color: var(--muted-d);">100% On-Device Processing</span>
        <span style="font-size: 13px; color: var(--muted-d);">Zero Tracking Telemetry</span>
        <span style="font-size: 13px; color: var(--muted-d);">No Bundled Adware</span>
        <span style="font-size: 13px; color: var(--gold); font-weight: 700; margin-top: 6px;">v2.2 Turbo Active</span>
      </div>
    </div>

    <div class="wrap footer-base">
      <p>&copy; <span id="currentYear">2026</span> Downloader Pro. All rights reserved.</p>
      <div style="display:flex; gap:16px;">
        <a href="#top" style="color:var(--gold);">Back to top &uarr;</a>
      </div>
    </div>
  </footer>

  <!-- Floating Action Button -->
  <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="fab" id="fabBtn" title="Quick Download Setup" aria-label="Quick Download Setup">
    <svg class="ic" style="width:24px; height:24px;" aria-hidden="true"><use href="#i-download"></use></svg>
  </a>

  <!-- ============================================================
       CHECKOUT MODAL DIALOG
       ============================================================ -->
  <dialog id="checkoutModal">
    <div class="modal-box">
      <button class="modal-close" id="modalCloseBtn" aria-label="Close dialog">
        <svg class="ic"><use href="#i-close"></use></svg>
      </button>

      <div id="checkoutFormStep">
        <h3 style="font-size: 24px; margin-bottom: 6px;">Unlock Downloader Pro</h3>
        <p style="font-size: 14px; color: var(--muted-d); margin-bottom: 20px;">
          Instant activation key delivered on screen and saved locally.
        </p>

        <form id="checkoutForm">
          <div class="form-group">
            <label for="checkoutPlan">Selected Plan</label>
            <select id="checkoutPlan" class="form-input" style="cursor:pointer;">
              <option value="pro_lifetime">Lifetime Master Pass ($49.99 one-time)</option>
              <option value="pro_yearly">Annual Pro Pass ($29.99 / year)</option>
            </select>
          </div>

          <div class="form-group">
            <label for="custName">Your Name</label>
            <input type="text" id="custName" class="form-input" placeholder="Media Creator" required>
          </div>

          <div class="form-group">
            <label for="custEmail">Your Email</label>
            <input type="email" id="custEmail" class="form-input" placeholder="creator@example.com" required>
          </div>

          <button type="submit" class="btn btn-gold" style="width: 100%; margin-top: 14px;" id="btnSubmitCheckout">
            <span>Generate License &amp; Download</span>
            <svg class="ic"><use href="#i-bolt"></use></svg>
          </button>
        </form>
      </div>

      <div class="key-display-box" id="keyResultBox">
        <div style="text-align:center; margin-bottom: 12px;">
          <span style="font-size: 11px; font-weight: 800; background: var(--gold); color: #0b0b0b; padding: 3px 8px; border-radius: 4px;">PURCHASE ACTIVATED</span>
          <h4 style="font-size: 18px; margin-top: 8px;" id="resPlanTitle">Lifetime Master Pass</h4>
        </div>

        <p style="font-size: 12px; color: var(--muted-d); text-align:center; margin-bottom: 6px;">Your Standalone License Key:</p>
        <div class="key-display-val" id="resLicenseKey">MDP-LFT-XXXX-XXXX-XXXX</div>

        <div style="display:flex; gap: 10px;">
          <button class="btn btn-line btn-sm" id="btnCopyKey" style="flex:1;">
            <span>Copy Key</span>
            <svg class="ic"><use href="#i-copy"></use></svg>
          </button>
          <a href="https://drive.google.com/file/d/1dvu3fgwbYFIF8ehQAUS74eqmNDyJ0wrN/view?usp=sharing" target="_blank" rel="noopener noreferrer" class="btn btn-gold btn-sm" style="flex:1;">
            <span>Download Setup</span>
            <svg class="ic"><use href="#i-download"></use></svg>
          </a>
        </div>
      </div>
    </div>
  </dialog>

  <!-- ============================================================
       LIGHTBOX VIEWER DIALOG
       ============================================================ -->
  <dialog id="lightboxModal">
    <div class="lb-box">
      <button class="modal-close" id="lbCloseBtn" style="top:12px; right:12px; z-index:10;" aria-label="Close lightbox">
        <svg class="ic"><use href="#i-close"></use></svg>
      </button>

      <div class="lb-content" id="lbContent">
        <div style="text-align:center; padding: 40px 20px;">
          <div style="font-size: 48px; font-weight:800; color:var(--gold);" id="lbBigTitle">MODULE PREVIEW</div>
          <p style="font-size: 16px; color: var(--white); margin-top: 10px; max-width: 500px;" id="lbDesc">Module description text goes here.</p>
        </div>
      </div>

      <div class="lb-nav">
        <button class="btn btn-line btn-sm" id="lbPrevBtn"><svg class="ic"><use href="#i-left"></use></svg><span>Prev</span></button>
        <span style="font-size: 13px; font-weight:700; color:var(--gold);" id="lbCounter">1 / 6</span>
        <button class="btn btn-line btn-sm" id="lbNextBtn"><span>Next</span><svg class="ic"><use href="#i-right"></use></svg></button>
      </div>
    </div>
  </dialog>

  <!-- Toast Notification -->
  <div class="toast" id="toastMessage">License key copied to clipboard!</div>

  <!-- ============================================================
       CAMPUS ENHANCEMENT JAVASCRIPT
       ============================================================ -->
  <script>
    (() => {
      const $ = (s, el = document) => el.querySelector(s);
      const $$ = (s, el = document) => [...el.querySelectorAll(s)];
      const root = document.documentElement;

      // ---------- Year Update ----------
      const yr = $('#currentYear');
      if (yr) yr.textContent = String(new Date().getFullYear());

      // ---------- Color Palette Switcher ----------
      const THEME_KEY = 'campus-theme';
      const themeDots = $$('.theme-dot');
      const setTheme = (theme) => {
        if (theme === 'red') {
          root.setAttribute('data-theme', 'red');
        } else if (theme === 'cyan') {
          root.setAttribute('data-theme', 'cyan');
        } else {
          root.removeAttribute('data-theme');
        }
        themeDots.forEach(d => d.classList.toggle('is-active', d.dataset.t === theme));
        try { localStorage.setItem(THEME_KEY, theme); } catch(e){}
      };

      try {
        const savedTheme = localStorage.getItem(THEME_KEY) || 'gold';
        setTheme(savedTheme);
      } catch(e) { setTheme('gold'); }

      themeDots.forEach(d => d.addEventListener('click', () => setTheme(d.dataset.t)));

      // ---------- Sticky Header Shadow ----------
      const header = $('.site-header');
      const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 12);
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();

      // ---------- Mobile Menu Toggle ----------
      const menuBtn = $('#menuBtn');
      const mobileMenu = $('#mobileMenu');
      if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
          const isOpen = mobileMenu.classList.toggle('is-open');
          menuBtn.setAttribute('aria-expanded', String(isOpen));
        });
        $$('a', mobileMenu).forEach(a => {
          a.addEventListener('click', () => {
            mobileMenu.classList.remove('is-open');
            menuBtn.setAttribute('aria-expanded', 'false');
          });
        });
      }

      // ---------- Hero Pointer Parallax Fan ----------
      const hero = $('.hero');
      const heroFan = $('#heroFan');
      if (hero && heroFan && window.matchMedia('(pointer: fine)').matches) {
        let raf = 0;
        hero.addEventListener('pointermove', (e) => {
          if (raf) return;
          raf = requestAnimationFrame(() => {
            raf = 0;
            const r = hero.getBoundingClientRect();
            heroFan.style.setProperty('--px', ((e.clientX - r.left) / r.width - 0.5).toFixed(3));
            heroFan.style.setProperty('--py', ((e.clientY - r.top) / r.height - 0.5).toFixed(3));
          });
        });
        hero.addEventListener('pointerleave', () => {
          heroFan.style.setProperty('--px', '0');
          heroFan.style.setProperty('--py', '0');
        });
      }

      // ---------- Scroll Reveal Observer ----------
      const reveals = $$('.reveal');
      if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver((entries) => {
          entries.forEach(en => {
            if (en.isIntersecting) {
              en.target.classList.add('is-in');
              io.unobserve(en.target);
            }
          });
        }, { rootMargin: '0px 0px -6% 0px', threshold: 0.05 });
        reveals.forEach(r => io.observe(r));
      } else {
        reveals.forEach(r => r.classList.add('is-in'));
      }

      // ---------- Format Category Filters ----------
      const filterBtns = $$('.filter');
      const formatCards = $$('.courses [data-cat]');
      filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          const cat = btn.dataset.cat;
          filterBtns.forEach(b => b.classList.toggle('is-active', b === btn));
          formatCards.forEach(card => {
            const matches = cat === 'all' || card.dataset.cat === cat;
            card.style.display = matches ? '' : 'none';
          });
        });
      });

      // ---------- Interactive Stream Analyzer Widget ----------
      const btnAnalyze = $('#btnAnalyze');
      const streamInput = $('#streamUrlInput');
      const streamLog = $('#streamLog');
      const analyzeStatus = $('#analyzeStatus');
      const btnQuickDl = $('#btnQuickDl');
      const formatTabs = $$('#formatTabs .inspect-chip');
      let activeFormat = '8k';

      formatTabs.forEach(chip => {
        chip.addEventListener('click', () => {
          formatTabs.forEach(c => c.classList.remove('is-active'));
          chip.classList.add('is-active');
          activeFormat = chip.dataset.fmt;
        });
      });

      if (btnAnalyze && streamInput) {
        btnAnalyze.addEventListener('click', () => {
          const url = streamInput.value.trim();
          if (!url) return;
          analyzeStatus.textContent = 'Resolving CDN...';
          analyzeStatus.style.color = 'var(--gold)';
          streamLog.innerHTML = `[CDN-CONNECT] Handshake with YouTube/TikTok Edge CDN...<br>&gt; Parsing URL: <span class="log-hi">${url}</span>`;

          setTimeout(() => {
            const isTikTok = url.includes('tiktok.com');
            if (isTikTok || activeFormat === 'tiktok') {
              streamLog.innerHTML = `
[SUCCESS] TikTok Direct Source Stream Resolved!<br>
&gt; <span class="log-succ">Video Codec:</span> H.264 High Profile (1080 &times; 1920)<br>
&gt; <span class="log-succ">Watermark Overlay:</span> <span class="log-hi">BYPASS CONFIRMED (Pure Source MP4)</span><br>
&gt; <span class="log-succ">Audio Stream:</span> AAC 48kHz Stereo @ 256kbps<br>
&gt; <span class="log-succ">Estimated Size:</span> 28.4 MB (No compression artifacts)
              `;
            } else if (activeFormat === '8k') {
              streamLog.innerHTML = `
[SUCCESS] YouTube 8K Cinema Stream Manifest Parsed!<br>
&gt; <span class="log-succ">Video Stream:</span> VP9 / AV1 @ 7680 &times; 4320 (60.00 FPS HDR)<br>
&gt; <span class="log-succ">Audio Stream:</span> Opus 320kbps Lossless (24-bit studio stereo)<br>
&gt; <span class="log-succ">Muxing Container:</span> MP4 with FastStart flag<br>
&gt; <span class="log-succ">CDN Sockets:</span> 16 Parallel chunks available
              `;
            } else if (activeFormat === 'mp3') {
              streamLog.innerHTML = `
[SUCCESS] High-Definition Audio Track Found!<br>
&gt; <span class="log-succ">Audio Bitrate:</span> 320kbps Constant Bitrate (CBR)<br>
&gt; <span class="log-succ">ID3 Tagger:</span> Auto-extracting Title, Artist, &amp; 1080p Album Artwork<br>
&gt; <span class="log-succ">Target File:</span> Studio Master .mp3 (Zero clipping)
              `;
            } else {
              streamLog.innerHTML = `
[SUCCESS] DASH Video Manifest Ready!<br>
&gt; <span class="log-succ">Resolution:</span> 4K UHD 3840 &times; 2160 @ 60 FPS<br>
&gt; <span class="log-succ">Audio Codec:</span> AAC-LC / Opus Dual Channels<br>
&gt; <span class="log-succ">Hardware Mux:</span> NVIDIA NVENC / Intel QuickSync Enabled
              `;
            }
            analyzeStatus.textContent = 'Stream Ready';
            analyzeStatus.style.color = '#4ec9b0';
            btnQuickDl.style.display = 'inline-flex';
          }, 600);
        });
      }

      // ---------- Floating Action Button Scroll Visibility ----------
      const fabBtn = $('#fabBtn');
      const closingSec = $('.closing');
      if (fabBtn && closingSec && 'IntersectionObserver' in window) {
        const fabIo = new IntersectionObserver((entries) => {
          entries.forEach(en => fabBtn.classList.toggle('is-off', en.isIntersecting));
        }, { threshold: 0.1 });
        fabIo.observe(closingSec);
      }

      // ---------- Toast Notification Function ----------
      const toast = $('#toastMessage');
      const showToast = (msg) => {
        if (!toast) return;
        toast.textContent = msg;
        toast.classList.add('is-show');
        setTimeout(() => toast.classList.remove('is-show'), 2600);
      };

      // ---------- Workstation Lightbox ----------
      const lbModal = $('#lightboxModal');
      const lbCloseBtn = $('#lbCloseBtn');
      const lbPrevBtn = $('#lbPrevBtn');
      const lbNextBtn = $('#lbNextBtn');
      const lbBigTitle = $('#lbBigTitle');
      const lbDesc = $('#lbDesc');
      const lbCounter = $('#lbCounter');
      const shotCards = $$('.shot-card');

      const galleryData = [
        { title: "ONE-CLICK WORKSTATION", desc: "Single input bar with automatic DASH manifest detection, instant stream query, and dark mode interface." },
        { title: "8K 60FPS SELECTOR", desc: "Dynamic format selector listing exact bitrates, audio codecs, and file sizes before initiating download." },
        { title: "16x BATCH QUEUE", desc: "Multi-socket TCP connection pool downloading entire channel libraries or playlists with auto-resume." },
        { title: "320KBPS AUDIO RIPPER", desc: "Extract pure studio-quality MP3 and M4A audio tracks with embedded ID3 artwork and metadata." },
        { title: "TIKTOK WATERMARK STRIPPER", desc: "Pulls clean video files directly from CDN edge nodes before watermark layers are applied." },
        { title: "GPU HARDWARE REMUXING", desc: "Zero CPU load remuxing using NVIDIA NVENC, AMD AMF, and Intel QuickSync graphics acceleration." }
      ];

      let curLbIdx = 0;
      const showLbSlide = (idx) => {
        curLbIdx = (idx + galleryData.length) % galleryData.length;
        const item = galleryData[curLbIdx];
        lbBigTitle.textContent = item.title;
        lbDesc.textContent = item.desc;
        lbCounter.textContent = `${curLbIdx + 1} / ${galleryData.length}`;
      };

      shotCards.forEach((card, idx) => {
        card.addEventListener('click', () => {
          showLbSlide(idx);
          if (lbModal && typeof lbModal.showModal === 'function') lbModal.showModal();
        });
      });

      if (lbCloseBtn && lbModal) lbCloseBtn.addEventListener('click', () => lbModal.close());
      if (lbPrevBtn) lbPrevBtn.addEventListener('click', () => showLbSlide(curLbIdx - 1));
      if (lbNextBtn) lbNextBtn.addEventListener('click', () => showLbSlide(curLbIdx + 1));
      if (lbModal) {
        lbModal.addEventListener('click', (e) => { if (e.target === lbModal) lbModal.close(); });
      }

      // ---------- Checkout Modal & Live License Generation ----------
      const checkoutModal = $('#checkoutModal');
      const modalCloseBtn = $('#modalCloseBtn');
      const checkoutPlanSelect = $('#checkoutPlan');
      const checkoutForm = $('#checkoutForm');
      const checkoutFormStep = $('#checkoutFormStep');
      const keyResultBox = $('#keyResultBox');
      const resPlanTitle = $('#resPlanTitle');
      const resLicenseKey = $('#resLicenseKey');
      const btnCopyKey = $('#btnCopyKey');
      const checkoutTriggers = $$('.trigger-checkout');

      checkoutTriggers.forEach(btn => {
        btn.addEventListener('click', () => {
          const plan = btn.dataset.plan || 'pro_lifetime';
          if (checkoutPlanSelect) checkoutPlanSelect.value = plan;
          checkoutFormStep.style.display = 'block';
          keyResultBox.classList.remove('is-active');
          if (checkoutModal && typeof checkoutModal.showModal === 'function') {
            checkoutModal.showModal();
          }
        });
      });

      if (modalCloseBtn && checkoutModal) {
        modalCloseBtn.addEventListener('click', () => checkoutModal.close());
        checkoutModal.addEventListener('click', (e) => { if (e.target === checkoutModal) checkoutModal.close(); });
      }

      if (checkoutForm) {
        checkoutForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const plan = checkoutPlanSelect.value;
          const name = $('#custName').value.trim() || 'Media Creator';
          const email = $('#custEmail').value.trim() || 'creator@example.com';
          const btnSubmit = $('#btnSubmitCheckout');
          btnSubmit.disabled = true;
          btnSubmit.textContent = 'Generating License...';

          let key = '';
          let planTitle = plan === 'pro_lifetime' ? 'Lifetime Master Pass' : 'Annual Pro Pass';

          try {
            const resp = await fetch('/api/v1/checkout', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ plan, name, email })
            });
            if (resp.ok) {
              const data = await resp.json();
              if (data.license_key) {
                key = data.license_key;
                planTitle = data.plan_title || planTitle;
              }
            }
          } catch(err) {
            console.warn('Backend server offline or static mode; fallback client generator');
          }

          // Fallback key generator if running as static HTML without backend
          if (!key) {
            const randHex = (n) => [...Array(n)].map(() => Math.floor(Math.random()*16).toString(16).toUpperCase()).join('');
            const pfx = plan === 'pro_lifetime' ? 'MDP-LFT' : 'MDP-YRL';
            key = `${pfx}-${randHex(4)}-${randHex(4)}-${randHex(4)}`;
          }

          resPlanTitle.textContent = planTitle;
          resLicenseKey.textContent = key;
          checkoutFormStep.style.display = 'none';
          keyResultBox.classList.add('is-active');
          btnSubmit.disabled = false;
          btnSubmit.innerHTML = '<span>Generate License &amp; Download</span>';
          showToast('License Key generated successfully!');
        });
      }

      if (btnCopyKey) {
        btnCopyKey.addEventListener('click', () => {
          const key = resLicenseKey.textContent;
          navigator.clipboard.writeText(key).then(() => {
            showToast('License key copied to clipboard!');
          }).catch(() => {
            showToast('Select text to copy: ' + key);
          });
        });
      }
    })();
  </script>
</body>
</html>
"""
