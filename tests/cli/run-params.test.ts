import { parseParams } from '../../src/cli/commands/run';

describe('run command params parser', () => {
  test('should parse JSON params', () => {
    const parsed = parseParams('{"duration":60,"start":10}');
    expect(parsed).toEqual({ duration: 60, start: 10 });
  });

  test('should parse key-value params', () => {
    const parsed = parseParams('duration=60,start=10,enabled=true,name=demo');
    expect(parsed).toEqual({
      duration: 60,
      start: 10,
      enabled: true,
      name: 'demo',
    });
  });

  test('should throw for invalid key-value params', () => {
    expect(() => parseParams('duration:60')).toThrow();
  });
});
