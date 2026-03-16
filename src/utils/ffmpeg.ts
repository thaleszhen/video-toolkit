// FFmpeg 封装
import ffmpeg from 'fluent-ffmpeg';
import { Logger } from './logger';

export class FFmpegWrapper {
  private logger: Logger;

  constructor() {
    this.logger = new Logger('FFmpeg');
  }

  async executeCommand(
    inputFile: string,
    outputFile: string,
    options: string[],
    onProgress?: (progress: number) => void
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      let command = ffmpeg(inputFile);

      options.forEach(opt => {
        command = command.inputOptions(opt);
      });

      command = command.output(outputFile);

      if (onProgress) {
        command.on('progress', (progress) => {
          const percent = progress.percent || 0;
          onProgress(percent);
        });
      }

      command
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
