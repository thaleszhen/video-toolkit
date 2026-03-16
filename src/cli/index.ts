// CLI 入口文件
import { Command } from 'commander';

const program = new Command();

program
  .name('video-toolkit')
  .description('AI 原生视频处理工具箱')
  .version('1.0.0');

program.parse(process.argv);
