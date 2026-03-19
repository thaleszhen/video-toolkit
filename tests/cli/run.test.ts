import { execSync } from 'child_process';

describe('Run Command', () => {
  test('should show run help', () => {
    const output = execSync('node dist/cli/index.js run --help', {
      encoding: 'utf-8',
    });
    expect(output).toContain('run');
    expect(output).toContain('--module');
    expect(output).toContain('--input');
    expect(output).toContain('--keep-download');
    expect(output).toContain('--download-dir');
  });

  test('should require module option', () => {
    let error: any;
    try {
      execSync('node dist/cli/index.js run', {
        encoding: 'utf-8',
      });
    } catch (e) {
      error = e;
    }
    expect(error).toBeDefined();
  });

  test('should show error for non-existent module', () => {
    let error: any;
    try {
      execSync('node dist/cli/index.js run --module nonexistent --input test.mp4', {
        encoding: 'utf-8',
      });
    } catch (e) {
      error = e;
    }
    expect(error).toBeDefined();
    const output = (error.stdout || '') + (error.stderr || '');
    expect(output).toContain('模块不存在');
  });

  test('should show error for missing input file', () => {
    let error: any;
    try {
      execSync(
        'node dist/cli/index.js run --module trim --input /nonexistent/file.mp4 --params duration=10',
        {
          encoding: 'utf-8',
          stdio: 'pipe',
        }
      );
    } catch (e) {
      error = e;
    }
    expect(error).toBeDefined();
    expect(error.status).toBe(1);
    const output = (error.stdout || '') + (error.stderr || '');
    expect(output).toContain('输入文件不存在');
  });
});
