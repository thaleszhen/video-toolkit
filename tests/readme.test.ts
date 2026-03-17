import fs from 'fs/promises';

describe('README Documentation', () => {
  test('README.md should exist', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('video-toolkit');
    expect(content).toContain('AI 原生视频处理工具箱');
  });

  test('should contain installation instructions', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('npm install');
  });

  test('should contain usage examples', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('video-toolkit workflow');
    expect(content).toContain('video-toolkit module list');
    expect(content).toContain('video-toolkit run');
  });

  test('should document core modules', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('trim');
    expect(content).toContain('crop');
    expect(content).toContain('compress');
    expect(content).toContain('watermark');
    expect(content).toContain('normalize');
  });

  test('should document presets', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('YouTube');
    expect(content).toContain('TikTok');
    expect(content).toContain('1920x1080');
    expect(content).toContain('1080x1920');
  });

  test('should contain development instructions', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('npm test');
    expect(content).toContain('npm run build');
  });

  test('should contain architecture overview', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('架构');
    expect(content).toContain('engine');
    expect(content).toContain('modules');
  });

  test('should have proper badges', async () => {
    const content = await fs.readFile('README.md', 'utf-8');
    expect(content).toContain('node');
    expect(content).toContain('typescript');
    expect(content).toContain('license');
  });
});
