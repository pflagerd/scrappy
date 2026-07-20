// inline-index-html.js
// Usage: node inline-index-html.js input.html output.html

import { readFile, writeFile } from 'fs/promises';
import path from 'path';

async function inlineindexhtml(inputPath, outputPath) {
  let html = await readFile(inputPath, 'utf-8');
  const baseDir = path.dirname(inputPath);

  // Inline CSS
  html = await inlineCssLinks(html, baseDir);

  // Inline JS
  html = await inlineJsScripts(html, baseDir);

  // Write output
  await writeFile(outputPath, html, 'utf-8');
  console.log(`Inlined HTML written to ${outputPath}`);
}

async function inlineCssLinks(html, baseDir) {
  // Matches: <link rel="stylesheet" href="style.css"> (with optional extra attributes)
  const cssLinkRegex = /<link\s+[^>]*rel=["']stylesheet["'][^>]*href=["']([^"':?#]+\.css)["'][^>]*>/gi;

  return await replaceAsync(html, cssLinkRegex, async (match, href) => {
    const cssPath = path.resolve(baseDir, href);
    try {
      const css = await readFile(cssPath, 'utf-8');
      return `<style>\n${css}\n</style>`;
    } catch {
      console.warn(`Warning: Could not inline CSS file: ${href}`);
      return match; // leave original if can't read
    }
  });
}

async function inlineJsScripts(html, baseDir) {
  // Matches: <script src="local.js"></script> (with optional extra attributes)
  const jsScriptRegex = /<script\s+[^>]*src=["']([^"':?#]+\.js)["'][^>]*>\s*<\/script>/gi;

  return await replaceAsync(html, jsScriptRegex, async (match, src) => {
    const jsPath = path.resolve(baseDir, src);
    try {
      const js = await readFile(jsPath, 'utf-8');
      return `<script>\n${js}\n</script>`;
    } catch {
      console.warn(`Warning: Could not inline JS file: ${src}`);
      return match;
    }
  });
}

// Helper for async regex replace
async function replaceAsync(str, regex, asyncFn) {
  const matches = [];
  str.replace(regex, (match, ...args) => {
    matches.push([match, ...args]);
    return match;
  });
  const replacements = await Promise.all(
    matches.map(args => asyncFn(...args))
  );
  let i = 0;
  return str.replace(regex, () => replacements[i++]);
}

// Entry point
if (process.argv.length !== 4) {
  console.log('Usage: node inline-index-html.js input.html output.html');
  process.exit(1);
}

const [,, inputPath, outputPath] = process.argv;
inlineindexhtml(inputPath, outputPath);
