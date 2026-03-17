import { Command } from 'commander';
import { ModuleRegistry } from '../../modules';

export const moduleCommand = new Command('module')
  .description('模块管理');

moduleCommand
  .command('list')
  .description('列出所有可用模块')
  .option('-c, --category <category>', '按类别筛选 (video, audio, core)')
  .action((options) => {
    let modules = ModuleRegistry.getAll();

    if (options.category) {
      modules = modules.filter(m => m.category === options.category);
    }

    if (modules.length === 0) {
      console.log('没有找到匹配的模块');
      return;
    }

    console.log('\n可用模块:\n');
    modules.forEach(module => {
      console.log(`  📦 ${module.name}`);
      console.log(`     描述: ${module.description}`);
      console.log(`     版本: ${module.version}`);
      console.log(`     类别: ${module.category}`);
      console.log('');
    });

    console.log(`总计: ${modules.length} 个模块\n`);
  });

moduleCommand
  .command('info <name>')
  .description('显示模块详细信息')
  .action((name) => {
    const module = ModuleRegistry.get(name);

    if (!module) {
      console.error(`❌ 模块不存在: ${name}`);
      process.exit(1);
    }

    console.log(`\n📦 模块: ${module.name}\n`);
    console.log(`描述: ${module.description}`);
    console.log(`版本: ${module.version}`);
    console.log(`类别: ${module.category}`);
    console.log(`\n输入格式:`);
    console.log(`  支持格式: ${module.input.accepts.join(', ')}`);
    console.log(`  必需参数: ${module.input.required.join(', ') || '无'}`);
    console.log(`  可选参数: ${module.input.optional.join(', ') || '无'}`);

    console.log(`\n参数详情:`);
    Object.entries(module.input.params).forEach(([key, param]) => {
      const required = param.required ? ' (必需)' : '';
      const defaultValue = param.default !== undefined ? ` [默认: ${param.default}]` : '';
      console.log(`  - ${key}${required}${defaultValue}`);
      console.log(`    类型: ${param.type}`);
      console.log(`    描述: ${param.description}`);
      if (param.enum) {
        console.log(`    可选值: ${param.enum.join(', ')}`);
      }
    });

    console.log(`\n输出格式: ${module.output.format}`);
    console.log(`输出文件名: ${module.output.filename}\n`);
  });
