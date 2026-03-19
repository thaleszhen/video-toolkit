import { Command } from 'commander';
import path from 'path';
import { WorkflowExecutor } from '../../engine/executor';
import { WorkflowParser } from '../../engine/parser';
import { WorkflowValidator } from '../../engine/validator';
import { resolveInputSource } from '../../utils/input-source';

export const workflowCommand = new Command('workflow')
  .description('使用预设工作流处理视频')
  .argument('<name>', '预设工作流名称 (youtube, tiktok)')
  .option('-i, --input <file>', '输入视频文件或 YouTube 链接', 'input.mp4')
  .option('-o, --output <file>', '输出视频文件', 'output.mp4')
  .option('--dry-run', '只验证工作流，不执行')
  .option('--verbose', '显示详细日志')
  .option('--keep-download', '保留 YouTube 下载源文件（默认自动清理）')
  .option('--download-dir <dir>', '下载目录（设置后自动保留源文件）')
  .action(async (name, options) => {
    console.log(`使用工作流: ${name}`);
    console.log(`输入文件: ${options.input}`);
    console.log(`输出文件: ${options.output}`);

    let resolvedInput:
      | {
          originalInput: string;
          resolvedInput: string;
          baseName: string;
          downloaded: boolean;
          cleanup: () => Promise<void>;
        }
      | undefined;
    let executor: WorkflowExecutor | undefined;

    try {
      const workflowPath = `src/presets/${name}.json`;
      const config = await WorkflowParser.parse(workflowPath);

      console.log(`\n工作流: ${config.name}`);
      console.log(`描述: ${config.description || '无'}`);
      console.log(`步骤数: ${config.steps.length}`);

      const validationResult = await WorkflowValidator.validate(config);
      if (!validationResult.valid) {
        console.error('\n❌ 工作流验证失败');
        validationResult.errors.forEach(err => {
          console.error(`  步骤 ${err.step}: ${err.error}`);
        });
        process.exit(1);
      }

      console.log('\n✅ 工作流验证通过');

      if (options.dryRun) {
        console.log('\n🔍 干运行模式 - 仅验证，不执行');
        console.log('\n步骤列表:');
        config.steps.forEach((step, index) => {
          console.log(`  ${index + 1}. ${step.name || step.module}`);
        });
        return;
      }

      const shouldKeepDownload = Boolean(options.keepDownload || options.downloadDir);
      resolvedInput = await resolveInputSource(options.input, {
        workingDir: process.cwd(),
        log: message => console.log(`  ↳ ${message}`),
        keepDownloadedSource: shouldKeepDownload,
        downloadDir: options.downloadDir,
      });

      if (resolvedInput.downloaded) {
        console.log(`下载文件: ${resolvedInput.resolvedInput}`);
      }

      executor = new WorkflowExecutor(config);
      const result = await executor.execute(resolvedInput.resolvedInput, options.output);

      if (result.success) {
        console.log('\n✅ 工作流执行成功！');
        console.log(`输出文件: ${result.outputFile}`);
        console.log(`绝对路径: ${path.resolve(result.outputFile)}`);
        console.log(`完成步骤: ${result.stepsCompleted}/${config.steps.length}`);
      }
    } catch (error: any) {
      console.error(`\n❌ 错误: ${error.message}`);
      process.exit(1);
    } finally {
      if (executor) {
        await executor.cleanup();
      }

      if (resolvedInput) {
        await resolvedInput.cleanup();
      }
    }
  });
