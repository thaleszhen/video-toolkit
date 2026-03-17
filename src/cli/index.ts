#!/usr/bin/env node

// CLI 入口文件
import { Command } from 'commander';
import { workflowCommand } from './commands/workflow';
import { moduleCommand } from './commands/module';
import { runCommand } from './commands/run';
import { createWorkflowCommand } from './commands/create-workflow';

const program = new Command();

program
  .name('video-toolkit')
  .description('AI 原生视频处理工具箱')
  .version('1.0.0');

program.addCommand(workflowCommand);
program.addCommand(moduleCommand);
program.addCommand(runCommand);
program.addCommand(createWorkflowCommand);

program.parse(process.argv);
