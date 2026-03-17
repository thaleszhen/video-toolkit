import { execSync } from 'child_process';

describe('Module Command', () => {
  test('should show module help', () => {
    const output = execSync('node dist/cli/index.js module --help', {
      encoding: 'utf-8'
    });
    expect(output).toContain('module');
    expect(output).toContain('模块管理');
  });

  test('should list modules', () => {
    const output = execSync('node dist/cli/index.js module list', {
      encoding: 'utf-8'
    });
    expect(output).toContain('可用模块');
    expect(output).toContain('trim');
    expect(output).toContain('crop');
    expect(output).toContain('compress');
    expect(output).toContain('watermark');
    expect(output).toContain('normalize');
  });

  test('should show module info', () => {
    const output = execSync('node dist/cli/index.js module info trim', {
      encoding: 'utf-8'
    });
    expect(output).toContain('trim');
    expect(output).toContain('裁剪视频时长');
    expect(output).toContain('duration');
  });

  test('should filter by category', () => {
    const output = execSync('node dist/cli/index.js module list --category video', {
      encoding: 'utf-8'
    });
    expect(output).toContain('trim');
    expect(output).toContain('crop');
    expect(output).not.toContain('normalize'); // audio category
  });
});
