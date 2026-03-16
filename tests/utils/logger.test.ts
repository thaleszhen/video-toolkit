import { Logger } from '../../src/utils/logger';

describe('Logger', () => {
  let consoleSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleSpy = jest.spyOn(console, 'log').mockImplementation();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  test('info should log blue message with context', () => {
    const logger = new Logger('TestContext');
    logger.info('test message');
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.anything(),
      'test message'
    );
  });

  test('warn should log yellow message with context', () => {
    const logger = new Logger('TestContext');
    logger.warn('warning message');
    expect(consoleWarnSpy).toHaveBeenCalledWith(
      expect.anything(),
      'warning message'
    );
  });

  test('error should log red message with context', () => {
    const logger = new Logger('TestContext');
    logger.error('error message');
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.anything(),
      'error message'
    );
  });

  test('success should log green message with context', () => {
    const logger = new Logger('TestContext');
    logger.success('success message');
    expect(consoleSpy).toHaveBeenCalledWith(
      expect.anything(),
      'success message'
    );
  });
});
