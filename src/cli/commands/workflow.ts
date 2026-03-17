import { Command } from 'commander';
import { WorkflowParser } from '../../engine/parser';
import { WorkflowValidator } from '../../engine/validator';
import { WorkflowExecutor } from '../../engine/executor';

export const workflowCommand = new Command('workflow')
  .description('使用预设工作流处理视频')
  .argument('<name>', '预设工作流名称 (youtube, tiktok)')
  .option('-i, --input <file>', '输入视频文件', 'input.mp4')
  .option('-o, --output <file>', '输出视频文件', 'output.mp4')
  .option('--dry-run', '只验证工作流，不执行')
  .option('--verbose', '显示详细日志')
  .action(async (name, options) => {
    console.log(`使用工作流: ${name}`);
    console.log(`输入文件: ${options.input}`);
    console.log(`输出文件: ${options.output}`);

    try {
      // 加载预设工作流
      const workflowPath = `src/presets/${name}.json`;
      const config = await WorkflowParser.parse(workflowPath);
      
      console.log(`\n工作流: ${config.name}`);
      console.log(`描述: ${config.description || '无'}`);
      console.log(`步骤数: ${config.steps.length}`);

      // 验证工作流
      const validationResult = await WorkflowValidator.validate(config);
      if (!validationResult.valid) {
        console.error('\n❌ 工作流验证失败:');
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

      // 执行工作流
      const executor = new WorkflowExecutor(config);
      const result = await executor.execute(options.input, options.output);

      if (result.success) {
        console.log(`\n✅ 工作流执行成功！`);
        console.log(`输出文件: ${result.outputFile}`);
        console.log(`完成步骤: ${result.stepsCompleted}/${config.steps.length}`);
      }

      await executor.cleanup();
    } catch (error: any) {
      console.error(`\n❌ 错误: ${error.message}`);
      process.exit(1);
    }
  });
