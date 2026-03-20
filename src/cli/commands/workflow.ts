import { Command } from 'commander';
import fs from 'fs/promises';
import path from 'path';
import { WorkflowExecutor } from '../../engine/executor';
import { WorkflowParser } from '../../engine/parser';
import { WorkflowValidator } from '../../engine/validator';
import { isSupportedVideoFile, resolveInputSource, sanitizeFileBaseName } from '../../utils/input-source';
import { buildBatchOutputPath, resolveWorkflowConfigPath } from '../../utils/workflow-config';

async function collectBatchInputs(inputDir: string): Promise<string[]> {
  const resolvedInputDir = path.resolve(inputDir);
  const entries = await fs.readdir(resolvedInputDir, { withFileTypes: true });

  return entries
    .filter(entry => entry.isFile() && isSupportedVideoFile(entry.name))
    .map(entry => path.join(resolvedInputDir, entry.name))
    .sort((a, b) => a.localeCompare(b));
}

function printWorkflowOverview(
  config: { name: string; description?: string; steps: Array<{ name?: string; module: string }> },
  workflowPath: string
) {
  console.log(`\n工作流: ${config.name}`);
  console.log(`描述: ${config.description || '无'}`);
  console.log(`配置文件: ${workflowPath}`);
  console.log(`步骤数: ${config.steps.length}`);
}

function printDryRunSteps(config: { steps: Array<{ name?: string; module: string }> }) {
  console.log('\n步骤列表:');
  config.steps.forEach((step, index) => {
    console.log(`  ${index + 1}. ${step.name || step.module}`);
  });
}

export const workflowCommand = new Command('workflow')
  .description('使用预设工作流处理视频')
  .argument('[name]', '预设工作流名称 (youtube, tiktok)，也可配合 --config 使用')
  .option('-i, --input <file>', '输入视频文件或 YouTube 链接')
  .option('-o, --output <file>', '输出视频文件')
  .option('--config <file>', '自定义工作流配置文件路径')
  .option('--input-dir <dir>', '批量处理目录中的视频文件')
  .option('--output-dir <dir>', '批量处理输出目录')
  .option('--dry-run', '只验证工作流，不执行')
  .option('--verbose', '显示详细日志')
  .option('--keep-download', '保留 YouTube 下载源文件（默认自动清理）')
  .option('--download-dir <dir>', '下载目录（设置后自动保留源文件）')
  .action(async (name, options) => {
    if (!name && !options.config) {
      console.error('❌ 请提供预设工作流名称或 --config <file>');
      process.exit(1);
    }

    if (options.input && options.inputDir) {
      console.error('❌ --input 和 --input-dir 不能同时使用');
      process.exit(1);
    }

    if (!options.dryRun && !options.input && !options.inputDir) {
      console.error('❌ 请提供 --input 或 --input-dir');
      process.exit(1);
    }

    if (options.inputDir && !options.dryRun && !options.outputDir) {
      console.error('❌ 批量处理需要指定 --output-dir');
      process.exit(1);
    }

    if (name) {
      console.log(`使用工作流: ${name}`);
    }
    if (options.config) {
      console.log(`工作流配置: ${options.config}`);
    }

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
      const workflowPath = await resolveWorkflowConfigPath({
        name,
        configPath: options.config,
        workingDir: process.cwd(),
      });
      const config = await WorkflowParser.parse(workflowPath);

      printWorkflowOverview(config, workflowPath);

      const validationResult = await WorkflowValidator.validate(config);
      if (!validationResult.valid) {
        console.error('\n❌ 工作流验证失败');
        validationResult.errors.forEach(err => {
          console.error(`  步骤 ${err.step}: ${err.error}`);
        });
        process.exit(1);
      }

      console.log('\n✅ 工作流验证通过');

      if (options.inputDir) {
        const batchInputs = await collectBatchInputs(options.inputDir);
        if (batchInputs.length === 0) {
          throw new Error(`目录中没有找到支持的视频文件: ${path.resolve(options.inputDir)}`);
        }

        console.log(`\n批量处理文件数: ${batchInputs.length}`);

        if (options.dryRun) {
          console.log('\n🔍 干运行模式 - 仅验证，不执行');
          printDryRunSteps(config);
          console.log('\n待处理文件:');
          batchInputs.forEach((file, index) => {
            const plannedOutput = options.outputDir
              ? buildBatchOutputPath(file, options.outputDir, config.name)
              : '(执行时需要 --output-dir)';
            console.log(`  ${index + 1}. ${path.basename(file)} -> ${plannedOutput}`);
          });
          return;
        }

        const resolvedOutputDir = path.resolve(options.outputDir);
        await fs.mkdir(resolvedOutputDir, { recursive: true });

        const successes: string[] = [];
        const failures: Array<{ input: string; error: string }> = [];

        for (let index = 0; index < batchInputs.length; index++) {
          const inputFile = batchInputs[index];
          const outputFile = buildBatchOutputPath(inputFile, resolvedOutputDir, config.name);

          console.log(`\n[${index + 1}/${batchInputs.length}] ${path.basename(inputFile)}`);
          console.log(`输出文件: ${outputFile}`);

          executor = new WorkflowExecutor(config);

          try {
            const result = await executor.execute(inputFile, outputFile);
            if (result.success) {
              successes.push(outputFile);
              console.log('  ✅ 处理成功');
            }
          } catch (error: any) {
            failures.push({
              input: inputFile,
              error: error?.message || String(error),
            });
            console.error(`  ❌ 处理失败: ${error?.message || String(error)}`);
          } finally {
            await executor.cleanup();
            executor = undefined;
          }
        }

        console.log('\n批量处理完成');
        console.log(`成功: ${successes.length}`);
        console.log(`失败: ${failures.length}`);
        console.log(`输出目录: ${resolvedOutputDir}`);

        if (failures.length > 0) {
          console.log('\n失败列表:');
          failures.forEach(item => {
            console.log(`  - ${path.basename(item.input)}: ${item.error}`);
          });
          process.exitCode = 1;
        }

        return;
      }

      if (options.dryRun) {
        console.log('\n🔍 干运行模式 - 仅验证，不执行');
        printDryRunSteps(config);
        return;
      }

      const outputFile = options.output || `${sanitizeFileBaseName(config.name)}-output.mp4`;
      console.log(`输入文件: ${options.input}`);
      console.log(`输出文件: ${outputFile}`);

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
      const result = await executor.execute(resolvedInput.resolvedInput, outputFile);

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
