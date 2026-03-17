import { WorkflowParser } from '../../src/engine/parser';
import { WorkflowValidator } from '../../src/engine/validator';

describe('TikTok Preset', () => {
  test('should parse TikTok preset', async () => {
    const config = await WorkflowParser.parse('src/presets/tiktok.json');
    expect(config.name).toBe('tiktok');
    expect(config.description).toContain('TikTok');
    expect(config.steps).toBeDefined();
    expect(config.steps.length).toBeGreaterThan(0);
  });

  test('should have 4 steps', async () => {
    const config = await WorkflowParser.parse('src/presets/tiktok.json');
    expect(config.steps).toHaveLength(4);
  });

  test('should validate TikTok preset', async () => {
    const config = await WorkflowParser.parse('src/presets/tiktok.json');
    const result = await WorkflowValidator.validate(config);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('should have correct step order', async () => {
    const config = await WorkflowParser.parse('src/presets/tiktok.json');

    expect(config.steps[0].module).toBe('trim');
    expect(config.steps[1].module).toBe('crop');
    expect(config.steps[2].module).toBe('normalize');
    expect(config.steps[3].module).toBe('compress');
  });

  test('should have correct parameters', async () => {
    const config = await WorkflowParser.parse('src/presets/tiktok.json');

    // Trim step
    expect(config.steps[0].params.duration).toBe(60);

    // Crop step - vertical video
    expect(config.steps[1].params.width).toBe(1080);
    expect(config.steps[1].params.height).toBe(1920);
    expect(config.steps[1].params.x).toBe('center');
    expect(config.steps[1].params.y).toBe('center');

    // Normalize step
    expect(config.steps[2].params.target).toBe('-14');

    // Compress step
    expect(config.steps[3].params.bitrate).toBe('5000k');
  });

  test('should be optimized for short vertical videos', async () => {
    const config = await WorkflowParser.parse('src/presets/tiktok.json');

    // Duration should be short (≤60s)
    expect(config.steps[0].params.duration).toBeLessThanOrEqual(60);

    // Should be vertical (height > width)
    expect(config.steps[1].params.height).toBeGreaterThan(config.steps[1].params.width);
  });
});
