import { calculateCropPosition, cropModule } from '../../src/modules/core/crop';

describe('Crop Module', () => {
  test('should have correct name', () => {
    expect(cropModule.name).toBe('crop');
  });

  test('should calculate centered crop position', () => {
    expect(calculateCropPosition('center', 'center')).toEqual({
      x: '(in_w-out_w)/2',
      y: '(in_h-out_h)/2',
    });
  });

  test('should calculate edge crop position', () => {
    expect(calculateCropPosition('right', 'bottom')).toEqual({
      x: 'in_w-out_w',
      y: 'in_h-out_h',
    });
  });

  test('should preserve numeric crop position', () => {
    expect(calculateCropPosition(12, 24)).toEqual({
      x: '12',
      y: '24',
    });
  });
});
