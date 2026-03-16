import { WorkflowExecutor } from '../../src/engine/executor';
import { WorkflowConfig } from '../../src/engine/parser';

describe('WorkflowExecutor', () => {
  test('should create instance with config', () => {
    const config: WorkflowConfig = {
      name: 'test-workflow',
      steps: []
    };
    const executor = new WorkflowExecutor(config);
    expect(executor).toBeInstanceOf(WorkflowExecutor);
  });

  test('should have execute method', () => {
    const config: WorkflowConfig = {
      name: 'test-workflow',
      steps: []
    };
    const executor = new WorkflowExecutor(config);
    expect(executor.execute).toBeDefined();
  });
});
