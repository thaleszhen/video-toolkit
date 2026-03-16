import fs from 'fs/promises';
import path from 'path';

describe('Project Initialization', () => {
  test('package.json should exist', async () => {
    const packageJson = await fs.readFile('package.json', 'utf-8');
    const pkg = JSON.parse(packageJson);
    expect(pkg.name).toBe('video-toolkit');
    expect(pkg.version).toBe('1.0.0');
  });

  test('tsconfig.json should exist', async () => {
    const tsconfig = await fs.readFile('tsconfig.json', 'utf-8');
    const config = JSON.parse(tsconfig);
    expect(config.compilerOptions.target).toBe('ES2022');
  });
});
