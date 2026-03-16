import { WorkflowParser, WorkflowConfig } from '../../src/engine/parser';
import fs from 'fs/promises';

describe('WorkflowParser', () => {
  test('should parse a valid workflow JSON', async () => {
    const jsonContent = JSON.stringify({
      name: 'test-workflow',
      description: 'test description',
      steps: [
        { module: 'trim', params: {} }
      ]
    });

    await fs.writeFile('/tmp/test-workflow.json', jsonContent);
    const config = await WorkflowParser.parse('/tmp/test-workflow.json');
    expect(config.name).toBe('test-workflow');
    expect(config.steps).toHaveLength(1);
  });

  test('should throw error if name is missing', async () => {
    const jsonContent = JSON.stringify({
      steps: []
    });

    await fs.writeFile('/tmp/test-workflow.json', jsonContent);
    await expect(WorkflowParser.parse('/tmp/test-workflow.json')).rejects.toThrow();
  });
});
