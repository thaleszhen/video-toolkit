import { execSync } from 'child_process';
import fs from 'fs/promises';
import os from 'os';
import path from 'path';

const tempDir = path.join(os.tmpdir(), 'video-toolkit-tests');
const testOutputFile = path.join(tempDir, 'test-workflow.json');

function quote(filePath: string) {
  return `"${filePath}"`;
}

describe('Create-Workflow Command', () => {
  beforeAll(async () => {
    await fs.mkdir(tempDir, { recursive: true });
  });

  beforeEach(async () => {
    try {
      await fs.unlink(testOutputFile);
    } catch {}
  });

  test('should show create-workflow help', () => {
    const output = execSync('node dist/cli/index.js create-workflow --help', {
      encoding: 'utf-8'
    });
    expect(output).toContain('create-workflow');
    expect(output).toContain('创建自定义工作流');
  });

  test('should create workflow file', async () => {
    const output = execSync(
      `node dist/cli/index.js create-workflow --name test-workflow --output ${quote(testOutputFile)}`,
      { encoding: 'utf-8' }
    );
    expect(output).toContain('工作流已创建');

    const content = await fs.readFile(testOutputFile, 'utf-8');
    const workflow = JSON.parse(content);
    expect(workflow.name).toBe('test-workflow');
    expect(workflow.version).toBe('1.0.0');
    expect(workflow.steps).toEqual([]);
  });

  test('should create workflow with description', async () => {
    const output = execSync(
      `node dist/cli/index.js create-workflow --name test --description "Test workflow" --output ${quote(testOutputFile)}`,
      { encoding: 'utf-8' }
    );
    expect(output).toContain('工作流已创建');

    const content = await fs.readFile(testOutputFile, 'utf-8');
    const workflow = JSON.parse(content);
    expect(workflow.description).toBe('Test workflow');
  });

  test('should create workflow from preset', async () => {
    const output = execSync(
      `node dist/cli/index.js create-workflow --name custom-youtube --from-preset youtube --output ${quote(testOutputFile)}`,
      { encoding: 'utf-8' }
    );
    expect(output).toContain('工作流已创建');
    expect(output).toContain('--config');

    const content = await fs.readFile(testOutputFile, 'utf-8');
    const workflow = JSON.parse(content);
    expect(workflow.name).toBe('custom-youtube');
    expect(workflow.steps.length).toBeGreaterThan(0);
  });

  test('should fail if file already exists', async () => {
    // 先创建一个文件
    await fs.writeFile(testOutputFile, '{}');

    let error: any;
    try {
      execSync(
        `node dist/cli/index.js create-workflow --name test --output ${quote(testOutputFile)}`,
        { encoding: 'utf-8', stdio: 'pipe' }
      );
    } catch (e) {
      error = e;
    }

    expect(error).toBeDefined();
    const output = (error.stdout || '') + (error.stderr || '');
    expect(output).toContain('文件已存在');
  });
});
