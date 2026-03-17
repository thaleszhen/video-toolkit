import { Command } from 'commander';
import fs from 'fs/promises';
import path from 'path';

export const createWorkflowCommand = new Command('create-workflow')
  .description('创建自定义工作流')
  .option('-n, --name <name>', '工作流名称', 'my-workflow')
  .option('-d, --description <desc>', '工作流描述', '')
  .option('-o, --output <file>', '输出文件路径', 'workflow.json')
  .option('--interactive', '交互式创建')
  .action(async (options) => {
    const workflow = {
      name: options.name,
      description: options.description,
      version: '1.0.0',
      steps: []
    };

    const outputPath = path.resolve(options.output);
    
    // 检查文件是否已存在
    try {
      await fs.access(outputPath);
      console.error(`❌ 文件已存在: ${outputPath}`);
      console.log('提示: 使用 --output 指定不同的输出路径\n');
      process.exit(1);
    } catch {}

    // 写入文件
    await fs.writeFile(outputPath, JSON.stringify(workflow, null, 2));

    console.log(`\n✅ 工作流已创建: ${outputPath}\n`);
    console.log('工作流配置:');
    console.log(JSON.stringify(workflow, null, 2));
    console.log('\n下一步:');
    console.log('1. 编辑工作流文件，添加处理步骤');
    console.log('2. 使用以下命令运行工作流:');
    console.log(`   video-toolkit workflow ${workflow.name} -i input.mp4 -o output.mp4\n`);
  });
