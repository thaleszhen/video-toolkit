import { VideoModule } from '../interface';
import { FFmpegWrapper } from '../../utils/ffmpeg';

export const trimModule: VideoModule = {
  name: 'trim',
  description: '裁剪视频时长',
  version: '1.0.0',
  category: 'video',
  input: {
    accepts: ['mp4', 'mov', 'avi', 'mkv'],
    required: ['duration'],
    optional: ['start', 'outputFormat'],
    params: {
      duration: {
        type: 'number',
        description: '裁剪时长（秒）',
        required: true,
      },
      start: {
        type: 'number',
        description: '开始时间（秒），默认为 0',
        default: 0,
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
    filename: 'trimmed-{name}',
    metadata: {
      duration: '裁剪后时长',
      originalDuration: '原始时长',
    },
  },
  async execute(input, params, context) {
    const { duration, start = 0 } = params;
    const ffmpeg = new FFmpegWrapper();

    const options = [
      '-ss', start.toString(),
      '-t', duration.toString(),
      '-c', 'copy'
    ];

    await ffmpeg.executeCommand(input, context.outputFile, options);
    return context.outputFile;
  },

  validate(params) {
    return params.duration > 0 && (params.start === undefined || params.start >= 0);
  },
};
