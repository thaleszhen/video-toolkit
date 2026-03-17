import { execSync } from 'child_process';

describe('Run Command', () => {
  test('should show run help', () => {
    const output = execSync('node dist/cli/index.js run --help', {
      encoding: 'utf-8'
    });
    expect(output).toContain('run');
    expect(output).toContain('运行单个模块');
  });

  test('should require module option', () => {
    let error: any;
    try {
      execSync('node dist/cli/index.js run', {
        encoding: 'utf-8'
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
        encoding: 'utf-8'
      });
    } catch (e) {
      error = e;
    }
    expect(error).toBeDefined();
    const output = error.stdout || error.stderr || error.message;
    expect(output).toContain('模块不存在');
  });

  test('should show error for missing input file', () => {
    let error: any;
    try {
      execSync('node dist/cli/index.js run --module trim --input /nonexistent/file.mp4 --params \'{"duration":10}\'', {
        encoding: 'utf-8',
        stdio: 'pipe'
      });
    } catch (e) {
      error = e;
    }
    expect(error).toBeDefined();
    expect(error.status).toBe(1);
    // stdout and stderr are available on the error object
    const output = (error.stdout || '') + (error.stderr || '');
    expect(output).toContain('输入文件不存在');
  });
});
