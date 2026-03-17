import { execSync } from 'child_process';

describe('Workflow Command', () => {
  test('should show workflow help', () => {
    const output = execSync('node dist/cli/index.js workflow --help', {
      encoding: 'utf-8'
    });
    expect(output).toContain('workflow');
    expect(output).toContain('预设工作流名称');
  });

  test('should show error for missing workflow name', () => {
    let error: any;
    try {
      execSync('node dist/cli/index.js workflow', {
        encoding: 'utf-8'
      });
    } catch (e) {
      error = e;
    }
    expect(error).toBeDefined();
    expect(error.stderr || error.stdout || error.message).toBeDefined();
  });
});
