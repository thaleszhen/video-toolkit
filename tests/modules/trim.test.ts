import { trimModule } from '../../src/modules/core/trim';

describe('Trim Module', () => {
  test('should have correct name', () => {
    expect(trimModule.name).toBe('trim');
  });

  test('should have required duration parameter', () => {
    expect(trimModule.input.required).toContain('duration');
  });

  test('execute should be defined', () => {
    expect(trimModule.execute).toBeDefined();
  });
});
