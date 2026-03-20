import { VideoModule } from '../interface';
import { FFmpegWrapper } from '../../utils/ffmpeg';

export const cropModule: VideoModule = {
  name: 'crop',
  description: '裁剪画面尺寸',
  version: '1.0.0',
  category: 'video',
  input: {
    accepts: ['mp4', 'mov', 'avi', 'mkv'],
    required: ['width', 'height'],
    optional: ['x', 'y', 'outputFormat'],
    params: {
      width: {
        type: 'number',
        description: '裁剪宽度（像素）',
        required: true,
      },
      height: {
        type: 'number',
        description: '裁剪高度（像素）',
        required: true,
      },
      x: {
        type: 'string',
        description: '水平位置',
        default: 'center',
        required: false,
      },
      y: {
        type: 'string',
        description: '垂直位置',
        default: 'center',
        required: false,
      },
      outputFormat: {
        type: 'string',
        description: '输出格式',
        enum: ['mp4', 'mov', 'avi'],
        default: 'mp4',
        required: false,
      },
    },
  },
  output: {
    format: 'mp4',
    filename: 'cropped-{name}',
    metadata: {
      width: '裁剪后宽度',
      height: '裁剪后高度',
    },
  },
  async execute(input, params, context) {
    const { width, height, x = 'center', y = 'center' } = params;
    const ffmpeg = new FFmpegWrapper();

    const cropParams = calculateCropPosition(x, y);

    const options = [
      '-vf', `crop=${width}:${height}:${cropParams.x}:${cropParams.y}`,
      '-c:v', 'libx264',
      '-preset', 'fast',
      '-crf', '23',
      '-c:a', 'copy'
    ];

    await ffmpeg.executeCommand(input, context.outputFile, options);
    return context.outputFile;
  },
};

function isNumericPosition(value: string | number): boolean {
  return typeof value === 'number' || /^-?\d+(\.\d+)?$/.test(String(value).trim());
}

function toCropExpression(value: string | number, axis: 'x' | 'y'): string {
  if (isNumericPosition(value)) {
    return String(value);
  }

  const normalized = String(value).trim().toLowerCase();
  if (axis === 'x') {
    if (normalized === 'center') {
      return '(in_w-out_w)/2';
    }
    if (normalized === 'left' || normalized === 'start') {
      return '0';
    }
    if (normalized === 'right' || normalized === 'end') {
      return 'in_w-out_w';
    }
  }

  if (normalized === 'center') {
    return '(in_h-out_h)/2';
  }
  if (normalized === 'top' || normalized === 'start') {
    return '0';
  }
  if (normalized === 'bottom' || normalized === 'end') {
    return 'in_h-out_h';
  }

  return String(value);
}

export function calculateCropPosition(x: string | number, y: string | number) {
  return {
    x: toCropExpression(x, 'x'),
    y: toCropExpression(y, 'y'),
  };
}
