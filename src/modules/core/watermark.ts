import { VideoModule } from '../interface';
import { FFmpegWrapper } from '../../utils/ffmpeg';

export const watermarkModule: VideoModule = {
  name: 'watermark',
  description: '添加水印',
  version: '1.0.0',
  category: 'video',
  input: {
    accepts: ['mp4', 'mov', 'avi', 'mkv'],
    required: ['text'],
    optional: ['position', 'fontSize', 'color', 'outputFormat'],
    params: {
      text: {
        type: 'string',
        description: '水印文本',
        required: true,
      },
      position: {
        type: 'string',
        description: '位置',
        enum: ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
        default: 'bottom-right',
        required: false,
      },
      fontSize: {
        type: 'number',
        description: '字体大小',
        default: 24,
        required: false,
      },
      color: {
        type: 'string',
        description: '颜色',
        default: 'white',
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
    filename: 'watermarked-{name}',
    metadata: {
      text: '水印文本',
    },
  },
  async execute(input, params, context) {
    const { text, position = 'bottom-right', fontSize = 24, color = 'white' } = params;
    const ffmpeg = new FFmpegWrapper();

    const positionCoords = calculatePosition(position);

    const options = [
      '-vf', `drawtext=text='${text}':fontcolor=${color}:fontsize=${fontSize}:x=${positionCoords.x}:y=${positionCoords.y}`,
      '-c:a', 'copy'
    ];

    await ffmpeg.executeCommand(input, context.outputFile, options);
    return context.outputFile;
  },
};

function calculatePosition(position: string) {
  const positions: { [key: string]: { x: string; y: string } } = {
    'top-left': { x: '10', y: '10' },
    'top-right': { x: '(w-tw-10)', y: '10' },
    'bottom-left': { x: '10', y: '(h-th-10)' },
    'bottom-right': { x: '(w-tw-10)', y: '(h-th-10)' },
    'center': { x: '(w-tw)/2', y: '(h-th)/2' },
  };
  return positions[position] || positions['bottom-right'];
}
