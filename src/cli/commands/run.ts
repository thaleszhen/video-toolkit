import { Command } from 'commander';
import * as fs from 'fs/promises';
import path from 'path';
import { ModuleRegistry } from '../../modules';
import { resolveInputSource } from '../../utils/input-source';
import { createManagedTempDir } from '../../utils/temp-dir';

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
  const pairs = raw
    .split(',')
    .map(item => item.trim())
    .filter(Boolean);

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
  .requiredOption('-i, --input <file>', '输入文件或 YouTube 链接')
  .option('-o, --output <file>', '输出文件')
  .option('--params <value>', '模块参数（JSON 或 key=value,key2=value2）')
  .option('--keep-download', '保留 YouTube 下载源文件（默认自动清理）')
  .option('--download-dir <dir>', '下载目录（设置后自动保留源文件）')
  .action(async options => {
    const module = ModuleRegistry.get(options.module);
    if (!module) {
      console.error(`❌ 模块不存在: ${options.module}`);
      process.exit(1);
    }

    console.log(`\n📦 运行模块: ${module.name}`);
    console.log(`描述: ${module.description}\n`);

    let params: Record<string, any> = {};
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

    const missingParams = module.input.required.filter(param => {
      const value = params[param];
      return value === undefined || value === null || value === '';
    });

    if (missingParams.length > 0) {
      console.error(`❌ 缺少必需参数: ${missingParams.join(', ')}`);
      console.log(`\n模块 ${module.name} 需要以下参数:`);
      Object.entries(module.input.params).forEach(([key, param]) => {
        if (param.required) {
          const defaultValue = param.default !== undefined ? ` [默认: ${param.default}]` : '';
          console.log(`  - ${key}${defaultValue}: ${param.description}`);
        }
      });
      process.exit(1);
    }

    Object.entries(module.input.params).forEach(([key, param]) => {
      if (params[key] === undefined && param.default !== undefined) {
        params[key] = param.default;
      }
    });

    if (module.validate && !module.validate(params)) {
      console.error(`❌ 模块参数校验失败: ${module.name}`);
      process.exit(1);
    }

    let commandTempDir: string | undefined;
    let resolvedInput:
      | {
          originalInput: string;
          resolvedInput: string;
          baseName: string;
          downloaded: boolean;
          cleanup: () => Promise<void>;
        }
      | undefined;
    let moduleError: unknown;

    try {
      const shouldKeepDownload = Boolean(options.keepDownload || options.downloadDir);
      resolvedInput = await resolveInputSource(options.input, {
        workingDir: process.cwd(),
        log: message => console.log(`  ↳ ${message}`),
        keepDownloadedSource: shouldKeepDownload,
        downloadDir: options.downloadDir,
      });

      const outputFile =
        options.output ||
        `${module.output.filename.replace('{name}', resolvedInput.baseName)}.${module.output.format}`;

      console.log(`输入: ${resolvedInput.originalInput}`);
      if (resolvedInput.downloaded) {
        console.log(`下载文件: ${resolvedInput.resolvedInput}`);
      }
      console.log(`输出: ${outputFile}\n`);

      commandTempDir = await createManagedTempDir('run');
      const context = {
        inputFile: resolvedInput.resolvedInput,
        outputFile,
        workingDir: process.cwd(),
        temporaryDir: commandTempDir,
        log: (message: string) => console.log(`  ↳ ${message}`),
        error: (message: string) => console.error(`  ❌ ${message}`),
      };

      if (module.preCheck) {
        const ok = await module.preCheck(context);
        if (!ok) {
          throw new Error('模块执行前检查失败');
        }
      }

      console.log('🚀 开始执行...\n');
      const result = await module.execute(resolvedInput.resolvedInput, params, context);
      console.log('\n✅ 执行成功！');
      console.log(`输出文件: ${result}`);
      console.log(`绝对路径: ${path.resolve(result)}\n`);
    } catch (error) {
      moduleError = error;
    } finally {
      if (module.cleanup) {
        module.cleanup();
      }

      if (commandTempDir) {
        await fs.rm(commandTempDir, { recursive: true, force: true });
      }

      if (resolvedInput) {
        await resolvedInput.cleanup();
      }
    }

    if (moduleError) {
      const message = moduleError instanceof Error ? moduleError.message : String(moduleError);
      console.error(`\n❌ 执行失败: ${message}\n`);
      process.exit(1);
    }
  });
