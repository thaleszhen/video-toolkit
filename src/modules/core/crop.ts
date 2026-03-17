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

    const cropParams = calculateCropPosition(x, y, width, height);

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

function calculateCropPosition(x: string, y: string, width: number, height: number) {
  return { x: 0, y: 0 };
}
