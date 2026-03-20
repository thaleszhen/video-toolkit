import { Command } from 'commander';
import fs from 'fs/promises';
import path from 'path';
import { WorkflowParser } from '../../engine/parser';
import { resolveWorkflowConfigPath } from '../../utils/workflow-config';

export const createWorkflowCommand = new Command('create-workflow')
  .description('创建自定义工作流')
  .option('-n, --name <name>', '工作流名称', 'my-workflow')
  .option('-d, --description <desc>', '工作流描述', '')
  .option('-o, --output <file>', '输出文件路径', 'workflow.json')
  .option('--from-preset <name>', '基于内置预设创建可编辑的工作流')
  .option('--interactive', '交互式创建')
  .action(async options => {
    try {
      let baseSteps: Array<Record<string, any>> = [];
      let baseDescription = options.description;

      if (options.fromPreset) {
        const presetPath = await resolveWorkflowConfigPath({
          name: options.fromPreset,
          workingDir: process.cwd(),
        });
        const preset = await WorkflowParser.parse(presetPath);
        baseSteps = JSON.parse(JSON.stringify(preset.steps || []));

        if (!baseDescription) {
          baseDescription = `基于 ${preset.name} 预设创建`;
        }
      }

      const workflow = {
        name: options.name,
        description: baseDescription,
        version: '1.0.0',
        steps: baseSteps,
      };

      const outputPath = path.resolve(options.output);

      try {
        await fs.access(outputPath);
        console.error(`❌ 文件已存在: ${outputPath}`);
        console.log('提示: 使用 --output 指定不同的输出路径\n');
        process.exit(1);
      } catch {}

      await fs.mkdir(path.dirname(outputPath), { recursive: true });
      await fs.writeFile(outputPath, JSON.stringify(workflow, null, 2));

      console.log(`\n✅ 工作流已创建: ${outputPath}\n`);
      console.log('工作流配置:');
      console.log(JSON.stringify(workflow, null, 2));
      console.log('\n下一步:');
      console.log('1. 编辑工作流文件，按你的交付场景调整步骤和参数');
      console.log('2. 使用以下命令运行工作流:');
      console.log(`   video-toolkit workflow --config "${outputPath}" -i input.mp4 -o output.mp4\n`);
    } catch (error: any) {
      console.error(`\n❌ 创建失败: ${error?.message || String(error)}\n`);
      process.exit(1);
    }
  });
