import { ModuleRegistry } from '../../src/modules';

describe('ModuleRegistry', () => {
  beforeEach(() => {
    // 清空注册表
    ModuleRegistry._clear();
  });

  test('should register a module', () => {
    const mockModule = {
      name: 'test-module',
      execute: async () => 'output.mp4'
    };
    ModuleRegistry.register(mockModule as any);
    const retrieved = ModuleRegistry.get('test-module');
    expect(retrieved).toBeDefined();
  });

  test('should retrieve a module by name', () => {
    const mockModule = {
      name: 'test-module',
      execute: async () => 'output.mp4'
    };
    ModuleRegistry.register(mockModule as any);
    const retrieved = ModuleRegistry.get('test-module');
    expect(retrieved?.name).toBe('test-module');
  });

  test('should return all modules', () => {
    ModuleRegistry.register({ name: 'module1', execute: async () => '' } as any);
    ModuleRegistry.register({ name: 'module2', execute: async () => '' } as any);
    const allModules = ModuleRegistry.getAll();
    expect(allModules).toHaveLength(2);
  });
});
