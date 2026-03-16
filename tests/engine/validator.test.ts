import { WorkflowValidator } from '../../src/engine/validator';
import { ModuleRegistry } from '../../src/modules';
import { VideoModule } from '../../src/modules/interface';

describe('WorkflowValidator', () => {
  beforeEach(() => {
    // 清空注册表
    ModuleRegistry._clear();
  });

  test('should validate a valid workflow', async () => {
    // 注册测试模块
    const testModule: VideoModule = {
      name: 'test-module',
      description: 'Test module',
      version: '1.0.0',
      category: 'core',
      input: {
        accepts: ['mp4'],
        required: [],
        optional: [],
        params: {}
      },
      output: {
        format: 'mp4',
        filename: 'output.mp4'
      },
      execute: async () => 'output.mp4'
    };
    ModuleRegistry.register(testModule);

    const config = {
      name: 'test-workflow',
      steps: [
        { module: 'test-module', params: {} }
      ]
    };

    const result = await WorkflowValidator.validate(config);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('should report error for missing module', async () => {
    const config = {
      name: 'test-workflow',
      steps: [
        { module: 'non-existent-module', params: {} }
      ]
    };

    const result = await WorkflowValidator.validate(config);
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });
});
