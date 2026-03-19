import {
  extractYouTubeVideoId,
  isHttpUrl,
  isYouTubeUrl,
  sanitizeFileBaseName,
} from '../../src/utils/input-source';

describe('input source utils', () => {
  test('should detect youtube watch url', () => {
    expect(isYouTubeUrl('https://www.youtube.com/watch?v=u2ah9tWTkmk')).toBe(true);
  });

  test('should detect youtube short url', () => {
    expect(isYouTubeUrl('https://youtu.be/u2ah9tWTkmk?si=abc')).toBe(true);
  });

  test('should reject non-youtube http url', () => {
    expect(isYouTubeUrl('https://example.com/video.mp4')).toBe(false);
    expect(isHttpUrl('https://example.com/video.mp4')).toBe(true);
  });

  test('should extract video id from watch url', () => {
    expect(extractYouTubeVideoId('https://www.youtube.com/watch?v=u2ah9tWTkmk&list=RD')).toBe(
      'u2ah9tWTkmk'
    );
  });

  test('should extract video id from youtu.be url', () => {
    expect(extractYouTubeVideoId('https://youtu.be/u2ah9tWTkmk?si=abc')).toBe('u2ah9tWTkmk');
  });

  test('should sanitize invalid filename chars', () => {
    expect(sanitizeFileBaseName(' youtube video: demo / 01 ')).toBe('youtube-video-demo-01');
  });
});
