import { WorkflowParser } from '../../src/engine/parser';
import { WorkflowValidator } from '../../src/engine/validator';

describe('YouTube Preset', () => {
  test('should parse YouTube preset', async () => {
    const config = await WorkflowParser.parse('src/presets/youtube.json');
    expect(config.name).toBe('youtube');
    expect(config.description).toContain('YouTube');
    expect(config.steps).toBeDefined();
    expect(config.steps.length).toBeGreaterThan(0);
  });

  test('should have 4 steps', async () => {
    const config = await WorkflowParser.parse('src/presets/youtube.json');
    expect(config.steps).toHaveLength(4);
  });

  test('should validate YouTube preset', async () => {
    const config = await WorkflowParser.parse('src/presets/youtube.json');
    const result = await WorkflowValidator.validate(config);
    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
  });

  test('should have correct step order', async () => {
    const config = await WorkflowParser.parse('src/presets/youtube.json');

    expect(config.steps[0].module).toBe('trim');
    expect(config.steps[1].module).toBe('crop');
    expect(config.steps[2].module).toBe('normalize');
    expect(config.steps[3].module).toBe('compress');
  });

  test('should have correct parameters', async () => {
    const config = await WorkflowParser.parse('src/presets/youtube.json');

    // Trim step
    expect(config.steps[0].params.duration).toBe(600);

    // Crop step
    expect(config.steps[1].params.width).toBe(1920);
    expect(config.steps[1].params.height).toBe(1080);
    expect(config.steps[1].params.x).toBe('center');
    expect(config.steps[1].params.y).toBe('center');

    // Normalize step
    expect(config.steps[2].params.target).toBe('-16');

    // Compress step
    expect(config.steps[3].params.bitrate).toBe('8000k');
  });
});
