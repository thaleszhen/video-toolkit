import fs from 'fs/promises';

describe('Directory Structure', () => {
  test('src/cli/index.ts should exist', async () => {
    await fs.access('src/cli/index.ts');
  });

  test('src/engine/parser.ts should exist', async () => {
    await fs.access('src/engine/parser.ts');
  });

  test('All module files should exist', async () => {
    const modules = ['trim', 'crop', 'compress', 'watermark', 'normalize'];
    for (const module of modules) {
      await fs.access(`src/modules/core/${module}.ts`);
    }
  });
});
