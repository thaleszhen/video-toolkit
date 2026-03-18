// FFmpeg 封装
import ffmpeg from 'fluent-ffmpeg';
import { Logger } from './logger';

let ffmpegConfigured = false;

function configureBinaryPaths() {
  if (ffmpegConfigured) {
    return;
  }

  let ffmpegPath = process.env.FFMPEG_PATH;
  let ffprobePath = process.env.FFPROBE_PATH;

  // Prefer explicit env vars, then fall back to local installer binaries.
  if (!ffmpegPath) {
    try {
      const installer = require('@ffmpeg-installer/ffmpeg') as { path?: string };
      ffmpegPath = installer.path;
    } catch {}
  }

  if (!ffprobePath) {
    try {
      const installer = require('@ffprobe-installer/ffprobe') as { path?: string };
      ffprobePath = installer.path;
    } catch {}
  }

  if (ffmpegPath) {
    ffmpeg.setFfmpegPath(ffmpegPath);
  }

  if (ffprobePath) {
    ffmpeg.setFfprobePath(ffprobePath);
  }

  ffmpegConfigured = true;
}

export class FFmpegWrapper {
  private logger: Logger;

  constructor() {
    this.logger = new Logger('FFmpeg');
    configureBinaryPaths();
  }

  async executeCommand(
    inputFile: string,
    outputFile: string,
    options: string[],
    onProgress?: (progress: number) => void
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      let command = ffmpeg(inputFile);

      // 解析选项并应用
      for (let i = 0; i < options.length; i++) {
        const opt = options[i];

        // 处理 -ss (seek)
        if (opt === '-ss' && i + 1 < options.length) {
          command = command.seekInput(options[i + 1]);
          i++; // 跳过下一个参数
        }
        // 处理 -t (duration)
        else if (opt === '-t' && i + 1 < options.length) {
          command = command.duration(parseFloat(options[i + 1]));
          i++; // 跳过下一个参数
        }
        // 处理 -c (codec)
        else if (opt === '-c' && i + 1 < options.length) {
          const codec = options[i + 1];
          if (codec === 'copy') {
            command = command.videoCodec('copy').audioCodec('copy');
          }
          i++; // 跳过下一个参数
        }
        // 处理 -c:v (video codec)
        else if (opt === '-c:v' && i + 1 < options.length) {
          command = command.videoCodec(options[i + 1]);
          i++;
        }
        // 处理 -c:a (audio codec)
        else if (opt === '-c:a' && i + 1 < options.length) {
          command = command.audioCodec(options[i + 1]);
          i++;
        }
        // 处理 -b:v (video bitrate)
        else if (opt === '-b:v' && i + 1 < options.length) {
          command = command.videoBitrate(options[i + 1]);
          i++;
        }
        // 处理 -b:a (audio bitrate)
        else if (opt === '-b:a' && i + 1 < options.length) {
          command = command.audioBitrate(options[i + 1]);
          i++;
        }
        // 处理 -preset
        else if (opt === '-preset' && i + 1 < options.length) {
          command = command.outputOptions(`-preset ${options[i + 1]}`);
          i++;
        }
        // 处理 -crf
        else if (opt === '-crf' && i + 1 < options.length) {
          command = command.outputOptions(`-crf ${options[i + 1]}`);
          i++;
        }
        // 处理 -vf (video filter)
        else if (opt === '-vf' && i + 1 < options.length) {
          command = command.videoFilters(options[i + 1]);
          i++;
        }
        // 处理 -af (audio filter)
        else if (opt === '-af' && i + 1 < options.length) {
          command = command.audioFilters(options[i + 1]);
          i++;
        }
        // 其他选项作为输出选项
        else if (opt.startsWith('-')) {
          // 跳过已处理的选项
        }
      }

      command = command.output(outputFile);

      if (onProgress) {
        command.on('progress', (progress) => {
          const percent = progress.percent || 0;
          onProgress(percent);
        });
      }

      command
        .on('start', (commandLine) => {
          this.logger.info(`Executing: ${commandLine}`);
        })
        .on('end', () => {
          this.logger.info(`FFmpeg completed: ${outputFile}`);
          resolve(outputFile);
        })
        .on('error', (err) => {
          this.logger.error(`FFmpeg error: ${err.message}`);
          reject(err);
        })
        .run();
    });
  }

  async getVideoInfo(filePath: string): Promise<any> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (err, metadata) => {
        if (err) {
          reject(err);
        } else {
          resolve(metadata);
        }
      });
    });
  }
}
