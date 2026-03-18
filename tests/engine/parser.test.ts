import { WorkflowParser, WorkflowConfig } from '../../src/engine/parser';
import fs from 'fs/promises';
import os from 'os';
import path from 'path';

const tempDir = path.join(os.tmpdir(), 'video-toolkit-tests');
const testWorkflowFile = path.join(tempDir, 'test-workflow.json');

describe('WorkflowParser', () => {
  beforeAll(async () => {
    await fs.mkdir(tempDir, { recursive: true });
  });

  afterEach(async () => {
    try {
      await fs.unlink(testWorkflowFile);
    } catch {}
  });

  test('should parse a valid workflow JSON', async () => {
    const jsonContent = JSON.stringify({
      name: 'test-workflow',
      description: 'test description',
      steps: [
        { module: 'trim', params: {} }
      ]
    });

    await fs.writeFile(testWorkflowFile, jsonContent);
    const config = await WorkflowParser.parse(testWorkflowFile);
    expect(config.name).toBe('test-workflow');
    expect(config.steps).toHaveLength(1);
  });

  test('should throw error if name is missing', async () => {
    const jsonContent = JSON.stringify({
      steps: []
    });

    await fs.writeFile(testWorkflowFile, jsonContent);
    await expect(WorkflowParser.parse(testWorkflowFile)).rejects.toThrow();
  });
});
