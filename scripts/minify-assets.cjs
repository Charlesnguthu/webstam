const fs = require('node:fs/promises');
const path = require('node:path');
const { minify } = require('terser');
const { transform } = require('lightningcss');

const assetsDir = path.join(__dirname, '..', 'static');

async function walk(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  const files = await Promise.all(entries.map((entry) => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(file) : [file];
  }));
  return files.flat();
}

async function main() {
  const files = (await walk(assetsDir)).filter((file) => /\.(?:js|css)$/.test(file));
  for (const file of files) {
    const code = await fs.readFile(file);
    if (file.endsWith('.js')) {
      const result = await minify(code.toString(), { compress: true, mangle: true });
      if (!result.code) throw new Error(`Terser produced no output for ${file}`);
      await fs.writeFile(file, result.code);
    } else {
      const result = transform({ filename: file, code, minify: true });
      await fs.writeFile(file, result.code);
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
