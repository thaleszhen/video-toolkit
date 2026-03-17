import { VideoModule } from '../interface';
import { FFmpegWrapper } from '../../utils/ffmpeg';

export const compressModule: VideoModule = {
  name: 'compress',
  description: '压缩视频',
  version: '1.0.0',
  category: 'video',
  input: {
    accepts: ['mp4', 'mov', 'avi', 'mkv'],
    required: ['bitrate'],
    optional: ['format'],
    params: {
      bitrate: {
        type: 'string',
        description: '比特率',
        required: true,
      },
      format: {
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
    filename: 'compressed-{name}',
    metadata: {
      bitrate: '比特率',
    },
  },
  async execute(input, params, context) {
    const { bitrate, format = 'mp4' } = params;
    const ffmpeg = new FFmpegWrapper();

    const options = [
      '-c:v', 'libx264',
      '-b:v', bitrate,
      '-preset', 'medium',
      '-crf', '23',
      '-c:a', 'aac',
      '-b:a', '128k'
    ];

    await ffmpeg.executeCommand(input, context.outputFile, options);
    return context.outputFile;
  },
};
