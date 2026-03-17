import { VideoModule } from '../interface';
import { FFmpegWrapper } from '../../utils/ffmpeg';

export const normalizeModule: VideoModule = {
  name: 'normalize',
  description: '音频标准化',
  version: '1.0.0',
  category: 'audio',
  input: {
    accepts: ['mp4', 'mov', 'avi', 'mkv'],
    required: ['target'],
    optional: [],
    params: {
      target: {
        type: 'string',
        description: '目标音量（LUFS）',
        required: true,
      },
    },
  },
  output: {
    format: 'mp4',
    filename: 'normalized-{name}',
    metadata: {
      target: '目标音量',
    },
  },
  async execute(input, params, context) {
    const { target } = params;
    const ffmpeg = new FFmpegWrapper();

    const options = [
      '-af', `loudnorm=I=${target}`,
      '-c:a', 'aac',
      '-b:a', '128k'
    ];

    await ffmpeg.executeCommand(input, context.outputFile, options);
    return context.outputFile;
  },
};
