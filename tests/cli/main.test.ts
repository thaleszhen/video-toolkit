import { execSync } from 'child_process';

describe('CLI Main Command', () => {
  test('should show version', () => {
    const output = execSync('node dist/cli/index.js --version', {
      encoding: 'utf-8'
    });
    expect(output).toContain('1.0.0');
  });

  test('should show help', () => {
    const output = execSync('node dist/cli/index.js --help', {
      encoding: 'utf-8'
    });
    expect(output).toContain('video-toolkit');
  });
});
