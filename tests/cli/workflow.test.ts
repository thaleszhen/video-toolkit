import { execSync } from 'child_process';
import fs from 'fs/promises';
import os from 'os';
import path from 'path';

const tempDir = path.join(os.tmpdir(), 'video-toolkit-workflow-tests');

function quote(filePath: string) {
  return `"${filePath}"`;
}

describe('Workflow Command', () => {
  beforeAll(async () => {
    await fs.mkdir(tempDir, { recursive: true });
  });

  test('should show workflow help', () => {
    const output = execSync('node dist/cli/index.js workflow --help', {
      encoding: 'utf-8',
    });
    expect(output).toContain('workflow');
    expect(output).toContain('--input');
    expect(output).toContain('--dry-run');
    expect(output).toContain('--keep-download');
    expect(output).toContain('--download-dir');
    expect(output).toContain('--config');
    expect(output).toContain('--input-dir');
    expect(output).toContain('--output-dir');
  });

  test('should show error for missing workflow name', () => {
    let error: any;
    try {
      execSync('node dist/cli/index.js workflow', {
        encoding: 'utf-8',
      });
    } catch (e) {
      error = e;
    }
    expect(error).toBeDefined();
    expect(error.stderr || error.stdout || error.message).toBeDefined();
  });

  test('should support custom workflow config in dry-run mode', async () => {
    const workflowPath = path.join(tempDir, 'custom-workflow.json');
    await fs.writeFile(
      workflowPath,
      JSON.stringify(
        {
          name: 'custom-workflow',
          description: 'custom test workflow',
          steps: [],
        },
        null,
        2
      )
    );

    const output = execSync(
      `node dist/cli/index.js workflow --config ${quote(workflowPath)} --dry-run`,
      { encoding: 'utf-8' }
    );

    expect(output).toContain('custom-workflow');
    expect(output).toContain('配置文件');
  });

  test('should preview batch files in dry-run mode', async () => {
    const workflowPath = path.join(tempDir, 'batch-workflow.json');
    const inputDir = path.join(tempDir, 'inputs');
    const outputDir = path.join(tempDir, 'outputs');

    await fs.mkdir(inputDir, { recursive: true });
    await fs.writeFile(
      workflowPath,
      JSON.stringify(
        {
          name: 'batch-workflow',
          steps: [],
        },
        null,
        2
      )
    );
    await fs.writeFile(path.join(inputDir, 'demo.mp4'), '');
    await fs.writeFile(path.join(inputDir, 'skip.txt'), '');

    const output = execSync(
      `node dist/cli/index.js workflow --config ${quote(workflowPath)} --input-dir ${quote(inputDir)} --output-dir ${quote(outputDir)} --dry-run`,
      { encoding: 'utf-8' }
    );

    expect(output).toContain('批量处理文件数');
    expect(output).toContain('demo.mp4');
    expect(output).not.toContain('skip.txt');
  });
});
