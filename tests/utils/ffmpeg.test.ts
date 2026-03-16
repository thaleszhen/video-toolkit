import { FFmpegWrapper } from '../../src/utils/ffmpeg';

describe('FFmpegWrapper', () => {
  let wrapper: FFmpegWrapper;

  beforeEach(() => {
    wrapper = new FFmpegWrapper();
  });

  test('should create instance', () => {
    expect(wrapper).toBeInstanceOf(FFmpegWrapper);
  });

  test('executeCommand should be defined', () => {
    expect(wrapper.executeCommand).toBeDefined();
  });

  test('getVideoInfo should be defined', () => {
    expect(wrapper.getVideoInfo).toBeDefined();
  });
});
