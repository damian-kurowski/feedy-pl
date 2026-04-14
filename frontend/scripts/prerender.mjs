// Prerender script — runs after `vite build`
// For each route in seo-routes.mjs, generates a static HTML file in dist/
// with unique title/description/canonical/JSON-LD/noscript content.
// The same Vue SPA bundle is loaded so the live experience is unchanged —
// only the initial HTML response (what crawlers see) differs per URL.

import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { routes } from './seo-routes.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const distDir = path.resolve(__dirname, '..', 'dist')
const templatePath = path.join(distDir, 'index.html')

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function escapeAttr(str) {
  return escapeHtml(str)
}

function renderJsonLdBlocks(jsonLd) {
  if (!jsonLd || jsonLd.length === 0) return ''
  return jsonLd
    .map((obj) => `<script type="application/ld+json">${JSON.stringify(obj)}</script>`)
    .join('\n    ')
}

function applyRoute(template, route) {
  let html = template

  // <title>
  html = html.replace(
    /<title>[^<]*<\/title>/,
    `<title>${escapeHtml(route.title)}</title>`,
  )

  // meta description
  html = html.replace(
    /<meta name="description" content="[^"]*"\s*\/>/,
    `<meta name="description" content="${escapeAttr(route.description)}" />`,
  )

  // meta keywords (optional)
  if (route.keywords) {
    html = html.replace(
      /<meta name="keywords" content="[^"]*"\s*\/>/,
      `<meta name="keywords" content="${escapeAttr(route.keywords)}" />`,
    )
  }

  // robots
  if (route.robots) {
    html = html.replace(
      /<meta name="robots" content="[^"]*"\s*\/>/,
      `<meta name="robots" content="${escapeAttr(route.robots)}" />`,
    )
  }

  // canonical
  html = html.replace(
    /<link rel="canonical" href="[^"]*"\s*\/>/,
    `<link rel="canonical" href="${escapeAttr(route.canonical)}" />`,
  )

  // og:url, og:title, og:description, twitter:title, twitter:description
  html = html.replace(
    /<meta property="og:url" content="[^"]*"\s*\/>/,
    `<meta property="og:url" content="${escapeAttr(route.canonical)}" />`,
  )
  html = html.replace(
    /<meta property="og:title" content="[^"]*"\s*\/>/,
    `<meta property="og:title" content="${escapeAttr(route.ogTitle || route.title)}" />`,
  )
  html = html.replace(
    /<meta property="og:description" content="[^"]*"\s*\/>/,
    `<meta property="og:description" content="${escapeAttr(route.ogDescription || route.description)}" />`,
  )
  html = html.replace(
    /<meta name="twitter:title" content="[^"]*"\s*\/>/,
    `<meta name="twitter:title" content="${escapeAttr(route.ogTitle || route.title)}" />`,
  )
  html = html.replace(
    /<meta name="twitter:description" content="[^"]*"\s*\/>/,
    `<meta name="twitter:description" content="${escapeAttr(route.ogDescription || route.description)}" />`,
  )

  // og:type
  if (route.ogType) {
    html = html.replace(
      /<meta property="og:type" content="[^"]*"\s*\/>/,
      `<meta property="og:type" content="${escapeAttr(route.ogType)}" />`,
    )
  }

  // Replace ALL JSON-LD blocks with route-specific ones
  // Strategy: drop existing JSON-LD blocks then insert new ones before </head>
  html = html.replace(
    /<!-- Structured Data:[\s\S]*?<\/script>\s*/g,
    '',
  )
  // Remove any leftover ld+json scripts (in case there are stray ones)
  html = html.replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>\s*/g, '')

  const jsonLdHtml = renderJsonLdBlocks(route.jsonLd)
  if (jsonLdHtml) {
    html = html.replace(/<\/head>/, `${jsonLdHtml}\n  </head>`)
  }

  // Replace noscript content (only if route provides one)
  if (route.noscript) {
    html = html.replace(
      /<noscript>[\s\S]*?<\/noscript>/,
      `<noscript>\n      <div style="max-width:800px;margin:0 auto;padding:40px 20px;font-family:system-ui,sans-serif">\n${route.noscript}\n      </div>\n    </noscript>`,
    )
  }

  return html
}

async function writeRouteHtml(route, content) {
  // Map paths to file paths:
  // /                                        → dist/index.html (do not overwrite, default)
  // /blog                                    → dist/blog.html
  // /blog/jak-dodac-produkty-do-ceneo        → dist/blog/jak-dodac-produkty-do-ceneo.html
  // /oferty/cennik                           → dist/oferty/cennik.html
  if (route.path === '/') {
    // Replace the default index.html with the homepage variant
    await fs.writeFile(path.join(distDir, 'index.html'), content, 'utf-8')
    return
  }
  const cleanPath = route.path.replace(/^\//, '')
  const filePath = path.join(distDir, `${cleanPath}.html`)
  await fs.mkdir(path.dirname(filePath), { recursive: true })
  await fs.writeFile(filePath, content, 'utf-8')
}

async function main() {
  let template
  try {
    template = await fs.readFile(templatePath, 'utf-8')
  } catch (e) {
    console.error(`[prerender] Cannot read template ${templatePath}:`, e.message)
    process.exit(1)
  }

  // Cache the original (unmodified) template for non-homepage routes
  // because the homepage route will overwrite dist/index.html.
  const originalTemplate = template

  // Save the unmodified template for backend dynamic rendering of /blog/:slug and /p/:slug
  await fs.writeFile(path.join(distDir, '__shell__.html'), originalTemplate, 'utf-8')

  console.log(`[prerender] Generating ${routes.length} static HTML files...`)

  for (const route of routes) {
    try {
      const html = applyRoute(originalTemplate, route)
      await writeRouteHtml(route, html)
      console.log(`  ✓ ${route.path}`)
    } catch (e) {
      console.error(`  ✗ ${route.path}: ${e.message}`)
      process.exitCode = 1
    }
  }

  console.log('[prerender] Done.')
}

main()
