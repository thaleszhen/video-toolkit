import { execSync } from 'child_process';
import fs from 'fs/promises';
import os from 'os';
import path from 'path';

const tempDir = path.join(os.tmpdir(), 'video-toolkit-tests');
const outputPath = path.join(tempDir, 'output.mp4');

function quote(filePath: string) {
  return `"${filePath}"`;
}

describe('End-to-End Workflow Execution', () => {
  const testVideoPath = 'tests/fixtures/test-video.mp4';

  beforeAll(async () => {
    await fs.mkdir(tempDir, { recursive: true });
  });

  beforeEach(async () => {
    // 清理输出文件
    try {
      await fs.unlink(outputPath);
    } catch {}
  });

  afterAll(async () => {
    // 清理测试文件
    try {
      await fs.unlink(outputPath);
    } catch {}
  });

  test('should validate workflow with dry-run', async () => {
    // 即使没有输入文件，dry-run 模式也应该工作
    let output: string;
    try {
      output = execSync(
        'node dist/cli/index.js workflow youtube --dry-run',
        { encoding: 'utf-8', timeout: 10000 }
      );
    } catch (error: any) {
      // 如果失败，捕获输出
      output = error.stdout || error.stderr || '';
    }

    // 应该显示工作流信息
    expect(output).toContain('youtube');
  });

  test('should list all modules', () => {
    const output = execSync(
      'node dist/cli/index.js module list',
      { encoding: 'utf-8' }
    );

    expect(output).toContain('trim');
    expect(output).toContain('crop');
    expect(output).toContain('compress');
    expect(output).toContain('watermark');
    expect(output).toContain('normalize');
  });

  test('should show module info', () => {
    const output = execSync(
      'node dist/cli/index.js module info compress',
      { encoding: 'utf-8' }
    );

    expect(output).toContain('compress');
    expect(output).toContain('压缩视频');
    expect(output).toContain('bitrate');
  });

  test('should create and validate custom workflow', async () => {
    const workflowPath = path.join(tempDir, 'test-custom-workflow.json');

    // 清理旧文件
    try {
      await fs.unlink(workflowPath);
    } catch {}

    // 创建工作流
    const createOutput = execSync(
      `node dist/cli/index.js create-workflow --name test-custom --output ${quote(workflowPath)}`,
      { encoding: 'utf-8' }
    );

    expect(createOutput).toContain('工作流已创建');

    // 验证文件内容
    const content = await fs.readFile(workflowPath, 'utf-8');
    const workflow = JSON.parse(content);
    expect(workflow.name).toBe('test-custom');

    // 清理
    await fs.unlink(workflowPath);
  });

  test('should handle invalid workflow name', () => {
    let error: any;
    try {
      execSync(
        'node dist/cli/index.js workflow nonexistent --dry-run',
        { encoding: 'utf-8', stdio: 'pipe' }
      );
    } catch (e) {
      error = e;
    }

    expect(error).toBeDefined();
    const output = (error.stdout || '') + (error.stderr || '');
    // 应该报错（文件不存在）
    expect(error.status).not.toBe(0);
  });

  test('should handle missing required parameters in run command', () => {
    let error: any;
    try {
      execSync(
        'node dist/cli/index.js run --module trim',
        { encoding: 'utf-8', stdio: 'pipe' }
      );
    } catch (e) {
      error = e;
    }

    expect(error).toBeDefined();
    // 应该报错（缺少必需参数）
    expect(error.status).not.toBe(0);
  });
});

describe('CLI Integration', () => {
  test('should show version', () => {
    const output = execSync(
      'node dist/cli/index.js --version',
      { encoding: 'utf-8' }
    );
    expect(output).toContain('1.0.0');
  });

  test('should show help', () => {
    const output = execSync(
      'node dist/cli/index.js --help',
      { encoding: 'utf-8' }
    );
    expect(output).toContain('video-toolkit');
    expect(output).toContain('AI 原生视频处理工具箱');
    expect(output).toContain('workflow');
    expect(output).toContain('module');
    expect(output).toContain('run');
    expect(output).toContain('create-workflow');
  });

  test('should show workflow help', () => {
    const output = execSync(
      'node dist/cli/index.js workflow --help',
      { encoding: 'utf-8' }
    );
    expect(output).toContain('预设工作流名称');
    expect(output).toContain('youtube');
    expect(output).toContain('tiktok');
  });

  test('should filter modules by category', () => {
    const videoOutput = execSync(
      'node dist/cli/index.js module list --category video',
      { encoding: 'utf-8' }
    );
    expect(videoOutput).toContain('trim');
    expect(videoOutput).toContain('crop');
    expect(videoOutput).not.toContain('normalize'); // audio category

    const audioOutput = execSync(
      'node dist/cli/index.js module list --category audio',
      { encoding: 'utf-8' }
    );
    expect(audioOutput).toContain('normalize');
    expect(audioOutput).not.toContain('trim');
  });
});
