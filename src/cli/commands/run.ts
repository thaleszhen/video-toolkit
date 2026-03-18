import { Command } from 'commander';
import { ModuleRegistry } from '../../modules';
import * as fs from 'fs/promises';
import path from 'path';

function coerceParamValue(value: string): any {
  const trimmed = value.trim();

  if (/^-?\d+(\.\d+)?$/.test(trimmed)) {
    return Number(trimmed);
  }

  if (trimmed.toLowerCase() === 'true') {
    return true;
  }

  if (trimmed.toLowerCase() === 'false') {
    return false;
  }

  if (trimmed.toLowerCase() === 'null') {
    return null;
  }

  return trimmed;
}

function parseKeyValueParams(raw: string): Record<string, any> {
  const result: Record<string, any> = {};
  const pairs = raw.split(',').map(item => item.trim()).filter(Boolean);

  if (pairs.length === 0) {
    throw new Error('参数为空');
  }

  for (const pair of pairs) {
    const separatorIndex = pair.indexOf('=');
    if (separatorIndex <= 0) {
      throw new Error(`无效参数格式: ${pair}`);
    }

    const key = pair.slice(0, separatorIndex).trim();
    const value = pair.slice(separatorIndex + 1);

    if (!key) {
      throw new Error(`无效参数键名: ${pair}`);
    }

    result[key] = coerceParamValue(value);
  }

  return result;
}

export function parseParams(raw?: string): Record<string, any> {
  if (!raw) {
    return {};
  }

  try {
    return JSON.parse(raw);
  } catch {
    return parseKeyValueParams(raw);
  }
}

export const runCommand = new Command('run')
  .description('运行单个模块')
  .requiredOption('-m, --module <name>', '模块名称')
  .requiredOption('-i, --input <file>', '输入文件')
  .option('-o, --output <file>', '输出文件')
  .option('--params <value>', '模块参数（JSON 或 key=value,key2=value2）')
  .action(async (options) => {
    const module = ModuleRegistry.get(options.module);
    if (!module) {
      console.error(`❌ 模块不存在: ${options.module}`);
      process.exit(1);
    }

    console.log(`\n📦 运行模块: ${module.name}`);
    console.log(`描述: ${module.description}\n`);

    // 检查输入文件是否存在
    try {
      await fs.access(options.input);
    } catch {
      console.error(`❌ 输入文件不存在: ${options.input}`);
      process.exit(1);
    }

    // 解析参数
    let params: any = {};
    if (options.params) {
      try {
        params = parseParams(options.params);
      } catch (error: any) {
        console.error(`❌ 参数解析失败: ${error.message}`);
        console.log('支持格式:');
        console.log('  1) JSON: {"duration": 60, "start": 10}');
        console.log('  2) 键值对: duration=60,start=10');
        process.exit(1);
      }
    }

    // 确定输出文件
    const inputFile = path.basename(options.input, path.extname(options.input));
    const outputFile = options.output || 
      module.output.filename.replace('{name}', inputFile) + '.' + module.output.format;

    console.log(`输入: ${options.input}`);
    console.log(`输出: ${outputFile}\n`);

    // 验证必需参数
    const missingParams = module.input.required.filter(param => {
      const value = params[param];
      return value === undefined || value === null || value === '';
    });
    if (missingParams.length > 0) {
      console.error(`❌ 缺少必需参数: ${missingParams.join(', ')}`);
      console.log(`\n模块 ${module.name} 需要以下参数:`);
      Object.entries(module.input.params).forEach(([key, param]) => {
        if (param.required) {
          const defaultVal = param.default !== undefined ? ` [默认: ${param.default}]` : '';
          console.log(`  - ${key}${defaultVal}: ${param.description}`);
        }
      });
      process.exit(1);
    }

    // 使用默认值填充可选参数
    Object.entries(module.input.params).forEach(([key, param]) => {
      if (params[key] === undefined && param.default !== undefined) {
        params[key] = param.default;
      }
    });

    // 创建执行上下文
    const temporaryDir = await fs.mkdtemp(path.join(process.cwd(), 'temp-'));
    const context = {
      inputFile: options.input,
      outputFile,
      workingDir: process.cwd(),
      temporaryDir,
      log: (message: string) => console.log(`  ℹ ${message}`),
      error: (message: string) => console.error(`  ❌ ${message}`),
    };

    try {
      // 执行前检查
      if (module.preCheck) {
        const ok = await module.preCheck(context);
        if (!ok) {
          throw new Error('模块执行前检查失败');
        }
      }

      console.log('🚀 开始执行...\n');
      
      // 执行模块
      const result = await module.execute(options.input, params, context);
      
      console.log(`\n✅ 执行成功！`);
      console.log(`输出文件: ${result}\n`);

      // 清理
      if (module.cleanup) {
        module.cleanup();
      }
      
      await fs.rm(temporaryDir, { recursive: true });
    } catch (error: any) {
      console.error(`\n❌ 执行失败: ${error.message}\n`);
      
      // 清理临时文件
      try {
        await fs.rm(temporaryDir, { recursive: true });
      } catch {}
      
      process.exit(1);
    }
  });
