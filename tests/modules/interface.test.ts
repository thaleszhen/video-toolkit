import { VideoModule, ExecutionContext } from '../../src/modules/interface';

describe('VideoModule Interface', () => {
  test('VideoModule interface should be defined', () => {
    const module: VideoModule = {
      name: 'test',
      description: 'test module',
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
    expect(module.name).toBe('test');
  });

  test('ExecutionContext interface should be defined', () => {
    const context: ExecutionContext = {
      inputFile: 'input.mp4',
      outputFile: 'output.mp4',
      temporaryDir: '/tmp',
      log: jest.fn(),
      error: jest.fn()
    };
    expect(context.inputFile).toBe('input.mp4');
  });
});
