# video-toolkit 设计文档

> **项目类型:** AI 原生视频处理工具箱
> **技术栈:** Node.js + TypeScript + Commander.js + FFmpeg
> **目标:** 3-6 个月内推向市场，支持 YouTube、TikTok 等平台
> **发布策略:** 小范围测试（10-20 核心用户内测）

---

## 第 1 部分：架构概览

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer                            │
│              (Commander.js 入口)                         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Workflow Engine                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Parser   │  │Validator │  │Executor  │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               Module System                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │Registry  │  │Discovery │  │Interface │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
┌────────▼────┐ ┌─────▼──────┐ ┌────▼─────┐
│   Core      │ │  Audio     │ │  Video   │
│  Modules    │ │  Modules   │ │ Modules  │
├─────────────┤ ├────────────┤ ├──────────┤
│• trim      │ │• normalize │ │• crop    │
│• watermark │ │• mix       │ │• resize  │
│• compress  │ │• denoise   │ │• convert │
└────────────┘ └────────────┘ └──────────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              FFmpeg Layer                                │
│           (fluent-ffmpeg 封装)                            │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. CLI Layer (`src/cli/`)
- **职责:** 命令行入口和用户交互
- **文件:** `src/cli/index.ts`
- **主命令:** `video-toolkit`
- **子命令:** `workflow`, `module`, `create-workflow`, `run`

#### 2. Workflow Engine (`src/engine/`)
- **职责:** 工作流解析、验证和执行
- **组件:**
  - **Parser:** 解析 JSON 工作流配置
  - **Validator:** 验证模块存在性、参数正确性
  - **Executor:** 按顺序执行模块，管理临时文件

#### 3. Module System (`src/modules/`)
- **职责:** 模块注册、发现和标准接口
- **组件:**
  - **Registry:** 模块注册表
  - **Discovery:** 自动发现和加载模块
  - **Interface:** 模块标准接口定义

#### 4. Core Modules (MVP)
- `trim`: 裁剪视频时长
- `crop`: 裁剪画面尺寸
- `compress`: 压缩视频
- `watermark`: 添加水印
- `normalize`: 音频标准化

### 目录结构（MVP）

```
video-toolkit/
├── src/
│   ├── cli/
│   │   ├── index.ts              # CLI 入口
│   │   └── commands/
│   │       ├── workflow.ts       # workflow 子命令
│   │       ├── module.ts         # module 子命令
│   │       ├── run.ts           # run 子命令
│   │       └── create-workflow.ts # create-workflow 子命令
│   ├── engine/
│   │   ├── parser.ts            # 工作流解析
│   │   ├── validator.ts         # 验证器
│   │   └── executor.ts          # 执行器
│   ├── modules/
│   │   ├── index.ts             # 模块注册
│   │   ├── interface.ts         # 模块接口定义
│   │   └── core/               # 核心模块
│   │       ├── trim.ts
│   │       ├── crop.ts
│   │       ├── compress.ts
│   │       ├── watermark.ts
│   │       └── normalize.ts
│   ├── presets/
│   │   ├── youtube.json         # YouTube 预设
│   │   └── tiktok.json         # TikTok 预设
│   └── utils/
│       ├── ffmpeg.ts            # FFmpeg 封装
│       └── logger.ts           # 日志工具
├── tests/
│   ├── engine/
│   │   ├── parser.test.ts
│   │   ├── validator.test.ts
│   │   └── executor.test.ts
│   └── modules/
│       ├── trim.test.ts
│       ├── crop.test.ts
│       └── core.test.ts
├── docs/
│   └── plans/
│       └── 2026-03-16-video-toolkit-design.md
├── package.json
├── tsconfig.json
└── README.md
```

---

## 第 2 部分：模块接口设计

### 模块标准接口

```typescript
// src/modules/interface.ts
export interface VideoModule {
  // 基本信息
  name: string;                    // 模块名称，如 'trim'
  description: string;             // 模块描述
  version: string;                 // 模块版本

  // 模块分类
  category: 'video' | 'audio' | 'core';

  // 输入定义
  input: {
    accepts: string[];             // 接受的文件格式
    required: string[];            // 必需参数
    optional: string[];            // 可选参数
    params: {                      // 参数详细配置
      [key: string]: {
        type: 'string' | 'number' | 'boolean' | 'file' | 'enum';
        description: string;
        enum?: string[];
        default?: any;
        required?: boolean;
      };
    };
  };

  // 输出定义
  output: {
    format: string;                // 输出文件格式
    filename: string;              // 输出文件名模式
    metadata?: { [key: string]: string | number }; // 元数据
  };

  // 核心方法
  execute: (input: string, params: any, context: ExecutionContext) => Promise<string>;
  validate?: (params: any) => boolean;
  preCheck?: (context: ExecutionContext) => Promise<boolean>;
  cleanup?: () => void;
}

export interface ExecutionContext {
  inputFile: string;
  outputFile: string;
  temporaryDir: string;
  log: (message: string) => void;
  error: (message: string) => void;
}
```

### 核心模块列表（MVP）

| 模块 | 名称 | 分类 | 功能描述 |
|------|------|------|----------|
| `trim` | 裁剪时长 | video | 裁剪视频到指定时长 |
| `crop` | 画面裁剪 | video | 裁剪视频画面尺寸和位置 |
| `compress` | 视频压缩 | video | 压缩视频大小和比特率 |
| `watermark` | 添加水印 | video | 添加文本或图片水印 |
| `normalize` | 音频标准化 | audio | 标准化音频音量（LUFS） |

### 模块注册系统

```typescript
// src/modules/index.ts
import { VideoModule } from './interface';

// 模块注册表
const moduleRegistry: Map<string, VideoModule> = new Map();

export class ModuleRegistry {
  // 注册模块
  static register(module: VideoModule) {
    moduleRegistry.set(module.name, module);
  }

  // 获取模块
  static get(name: string): VideoModule | undefined {
    return moduleRegistry.get(name);
  }

  // 获取所有模块
  static getAll(): VideoModule[] {
    return Array.from(moduleRegistry.values());
  }

  // 按分类列出模块
  static listByCategory(category: string): VideoModule[] {
    return this.getAll().filter(m => m.category === category);
  }
}
```

### FFmpeg 封装工具

```typescript
// src/utils/ffmpeg.ts
import ffmpeg from 'fluent-ffmpeg';
import { Logger } from './logger';

export class FFmpegWrapper {
  private logger: Logger;

  constructor() {
    this.logger = new Logger('FFmpeg');
  }

  // 执行 FFmpeg 命令
  async executeCommand(
    inputFile: string,
    outputFile: string,
    options: string[],
    onProgress?: (progress: number) => void
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      let command = ffmpeg(inputFile);

      // 应用选项
      options.forEach(opt => {
        command = command.inputOptions(opt);
      });

      // 输出文件
      command = command.output(outputFile);

      // 进度回调
      if (onProgress) {
        command.on('progress', (progress) => {
          const percent = progress.percent || 0;
          onProgress(percent);
        });
      }

      // 执行
      command
        .on('end', () => {
          this.logger.info(`FFmpeg completed: ${outputFile}`);
          resolve(outputFile);
        })
        .on('error', (err) => {
          this.logger.error(`FFmpeg error: ${err.message}`);
          reject(err);
        })
        .run();
    });
  }

  // 获取视频信息
  async getVideoInfo(filePath: string): Promise<any> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(filePath, (err, metadata) => {
        if (err) {
          reject(err);
        } else {
          resolve(metadata);
        }
      });
    });
  }
}
```

### 日志工具

```typescript
// src/utils/logger.ts
import chalk from 'chalk';

export class Logger {
  private context: string;

  constructor(context: string) {
    this.context = context;
  }

  info(message: string) {
    console.log(chalk.blue(`[${this.context}]`), message);
  }

  warn(message: string) {
    console.warn(chalk.yellow(`[${this.context}]`), message);
  }

  error(message: string) {
    console.error(chalk.red(`[${this.context}]`), message);
  }

  success(message: string) {
    console.log(chalk.green(`[${this.context}]`), message);
  }
}
```

---

## 第 3 部分：工作流引擎

### Parser（工作流解析）

```typescript
// src/engine/parser.ts
import fs from 'fs/promises';
import { ModuleRegistry } from '../modules';

export interface WorkflowConfig {
  name: string;
  description?: string;
  version?: string;
  steps: WorkflowStep[];
}

export interface WorkflowStep {
  module: string;
  params: Record<string, any>;
  name?: string;
  enabled?: boolean;
}

export class WorkflowParser {
  static async parse(filePath: string): Promise<WorkflowConfig> {
    const content = await fs.readFile(filePath, 'utf-8');
    const config = JSON.parse(content);

    // 验证必需字段
    if (!config.name) {
      throw new Error('Workflow config must have a name');
    }
    if (!config.steps || !Array.isArray(config.steps)) {
      throw new Error('Workflow config must have steps array');
    }

    return config;
  }

  static parseFromJSON(jsonString: string): WorkflowConfig {
    const config = JSON.parse(jsonString);
    return config;
  }
}
```

### Validator（工作流验证）

```typescript
// src/engine/validator.ts
import { WorkflowConfig, WorkflowStep } from './parser';
import { ModuleRegistry } from '../modules';

export interface ValidationError {
  step: number;
  module: string;
  error: string;
}

export class WorkflowValidator {
  static async validate(
    config: WorkflowConfig
  ): Promise<{ valid: boolean; errors: ValidationError[] }> {
    const errors: ValidationError[] = [];

    // 验证每个步骤
    for (let i = 0; i < config.steps.length; i++) {
      const step = config.steps[i];
      const stepErrors = await this.validateStep(step, i);
      errors.push(...stepErrors);
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  private static async validateStep(
    step: WorkflowStep,
    index: number
  ): Promise<ValidationError[]> {
    const errors: ValidationError[] = [];

    // 检查模块是否存在
    const module = ModuleRegistry.get(step.module);
    if (!module) {
      errors.push({
        step: index,
        module: step.module,
        error: `Module '${step.module}' not found`,
      });
      return errors;
    }

    // 检查必需参数
    for (const requiredParam of module.input.required) {
      if (!step.params[requiredParam]) {
        errors.push({
          step: index,
          module: step.module,
          error: `Missing required parameter: ${requiredParam}`,
        });
      }
    }

    // 检查参数类型
    for (const [paramName, paramConfig] of Object.entries(module.input.params)) {
      const value = step.params[paramName];
      if (value !== undefined && paramConfig.required && !this.validateType(value, paramConfig.type)) {
        errors.push({
          step: index,
          module: step.module,
          error: `Parameter '${paramName}' has invalid type: expected ${paramConfig.type}`,
        });
      }
    }

    return errors;
  }

  private static validateType(value: any, type: string): boolean {
    switch (type) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number';
      case 'boolean':
        return typeof value === 'boolean';
      default:
        return true;
    }
  }
}
```

### Executor（工作流执行）

```typescript
// src/engine/executor.ts
import { WorkflowConfig } from './parser';
import { ModuleRegistry } from '../modules';
import * as fs from 'fs/promises';
import path from 'path';
import { Logger } from '../utils/logger';

export interface ExecutionContext {
  inputFile: string;
  outputFile: string;
  workingDir: string;
  temporaryDir: string;
  log: (message: string) => void;
  error: (message: string) => void;
}

export class WorkflowExecutor {
  private logger: Logger;
  private temporaryFiles: string[] = [];

  constructor(private config: WorkflowConfig) {
    this.logger = new Logger('WorkflowExecutor');
  }

  async execute(
    inputFile: string,
    outputFile: string
  ): Promise<{ success: boolean; outputFile: string; stepsCompleted: number }> {
    this.logger.info(`Starting workflow: ${this.config.name}`);
    this.logger.info(`Input: ${inputFile}, Output: ${outputFile}`);

    // 创建临时目录
    const temporaryDir = await fs.mkdtemp(path.join(process.cwd(), 'temp-'));
    this.temporaryFiles.push(temporaryDir);

    let currentInput = inputFile;
    let stepsCompleted = 0;

    for (let i = 0; i < this.config.steps.length; i++) {
      const step = this.config.steps[i];

      // 检查步骤是否启用
      if (step.enabled === false) {
        this.logger.info(`Skipping disabled step: ${step.module}`);
        continue;
      }

      // 获取模块
      const module = ModuleRegistry.get(step.module);
      if (!module) {
        throw new Error(`Module not found: ${step.module}`);
      }

      // 构建输出文件路径
      const isLastStep = i === this.config.steps.length - 1;
      const stepOutputFile = isLastStep
        ? outputFile
        : path.join(temporaryDir, `${step.module}-${i}-${path.basename(inputFile)}`);

      // 构建执行上下文
      const context: ExecutionContext = {
        inputFile: currentInput,
        outputFile: stepOutputFile,
        workingDir: temporaryDir,
        temporaryDir,
        log: (message: string) => this.logger.info(message),
        error: (message: string) => this.logger.error(message),
      };

      // 前置检查
      if (module.preCheck) {
        const ok = await module.preCheck(context);
        if (!ok) {
          throw new Error(`Pre-check failed for module: ${step.module}`);
        }
      }

      // 执行模块
      this.logger.info(`Executing step ${i + 1}/${this.config.steps.length}: ${step.module}`);
      await module.execute(currentInput, step.params, context);

      // 更新当前输入
      currentInput = stepOutputFile;
      stepsCompleted++;
    }

    this.logger.info(`Workflow completed: ${stepsCompleted}/${this.config.steps.length} steps`);

    return {
      success: true,
      outputFile,
      stepsCompleted,
    };
  }

  async cleanup() {
    for (const file of this.temporaryFiles) {
      try {
        await fs.rm(file, { recursive: true });
      } catch (error) {
        this.logger.warn(`Failed to cleanup temporary file: ${file}`);
      }
    }
  }
}
```

### 预设工作流示例

#### YouTube 预设

```json
// src/presets/youtube.json
{
  "name": "youtube",
  "description": "YouTube 视频工作流",
  "version": "1.0.0",
  "steps": [
    {
      "module": "trim",
      "name": "裁剪时长",
      "params": {
        "duration": 600,
        "outputFormat": "mp4"
      }
    },
    {
      "module": "crop",
      "name": "裁剪画面",
      "params": {
        "width": 1920,
        "height": 1080,
        "x": "center",
        "y": "center"
      }
    },
    {
      "module": "normalize",
      "name": "音频标准化",
      "params": {
        "target": "-16LUFS"
      }
    },
    {
      "module": "compress",
      "name": "压缩视频",
      "params": {
        "bitrate": "8000k",
        "format": "mp4"
      }
    }
  ]
}
```

#### TikTok 预设

```json
// src/presets/tiktok.json
{
  "name": "tiktok",
  "description": "TikTok 视频工作流",
  "version": "1.0.0",
  "steps": [
    {
      "module": "trim",
      "name": "裁剪时长",
      "params": {
        "duration": 60,
        "outputFormat": "mp4"
      }
    },
    {
      "module": "crop",
      "name": "裁剪为竖屏",
      "params": {
        "width": 1080,
        "height": 1920,
        "x": "center",
        "y": "center"
      }
    },
    {
      "module": "normalize",
      "name": "音频标准化",
      "params": {
        "target": "-14LUFS"
      }
    },
    {
      "module": "compress",
      "name": "压缩视频",
      "params": {
        "bitrate": "5000k",
        "format": "mp4"
      }
    }
  ]
}
```

---

## 第 4 部分：CLI 接口设计

### 主命令结构

```typescript
// src/cli/index.ts
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

// 注册子命令
program.addCommand(workflowCommand);
program.addCommand(moduleCommand);
program.addCommand(runCommand);
program.addCommand(createWorkflowCommand);

program.parse(process.argv);
```

### 子命令设计

#### 1. `workflow` 命令 - 使用预设工作流

```typescript
// src/cli/commands/workflow.ts
import { Command } from 'commander';
import path from 'path';
import { WorkflowParser, WorkflowValidator, WorkflowExecutor } from '../../engine';

export const workflowCommand = new Command('workflow')
  .description('使用预设工作流处理视频')
  .argument('<name>', '预设工作流名称 (youtube, tiktok)')
  .option('-i, --input <file>', '输入视频文件', 'input.mp4')
  .option('-o, --output <file>', '输出视频文件', 'output.mp4')
  .option('--dry-run', '只验证工作流，不执行')
  .option('--verbose', '显示详细日志')
  .action(async (name, options) => {
    const presetPath = path.join(__dirname, '../../presets', `${name}.json`);

    try {
      // 解析工作流
      const config = await WorkflowParser.parse(presetPath);

      // 验证工作流
      const { valid, errors } = await WorkflowValidator.validate(config);
      if (!valid) {
        console.error('工作流验证失败:');
        errors.forEach(err => {
          console.error(`  步骤 ${err.step + 1}: ${err.error}`);
        });
        process.exit(1);
      }

      if (options.dryRun) {
        console.log('工作流验证通过！');
        console.log(`工作流: ${config.name}`);
        console.log(`描述: ${config.description}`);
        console.log(`步骤数: ${config.steps.length}`);
        return;
      }

      // 执行工作流
      const executor = new WorkflowExecutor(config);
      const result = await executor.execute(options.input, options.output);

      console.log('工作流执行完成！');
      console.log(`输出文件: ${result.outputFile}`);
      console.log(`完成步骤: ${result.stepsCompleted}`);

      // 清理临时文件
      await executor.cleanup();
    } catch (error) {
      console.error('执行失败:', error.message);
      process.exit(1);
    }
  });
```

#### 2. `module` 命令 - 模块管理

```typescript
// src/cli/commands/module.ts
import { Command } from 'commander';
import { ModuleRegistry } from '../../modules';

export const moduleCommand = new Command('module')
  .description('模块管理');

// 列出所有模块
moduleCommand
  .command('list')
  .description('列出所有可用模块')
  .option('-c, --category <category>', '按分类过滤')
  .action((options) => {
    const modules = options.category
      ? ModuleRegistry.listByCategory(options.category)
      : ModuleRegistry.getAll();

    console.log('\n可用模块:');
    console.log('─'.repeat(60));

    modules.forEach(module => {
      console.log(`\n${module.name} (${module.version})`);
      console.log(`  ${module.description}`);
      console.log(`  分类: ${module.category}`);
      console.log(`  接受格式: ${module.input.accepts.join(', ')}`);
    });

    console.log('\n' + '─'.repeat(60));
  });

// 查看模块详情
moduleCommand
  .command('show')
  .description('查看模块详细信息')
  .argument('<name>', '模块名称')
  .action((name) => {
    const module = ModuleRegistry.get(name);

    if (!module) {
      console.error(`模块不存在: ${name}`);
      process.exit(1);
    }

    console.log(`\n模块: ${module.name} (${module.version})`);
    console.log(`描述: ${module.description}`);
    console.log(`分类: ${module.category}`);

    console.log('\n必需参数:');
    for (const param of module.input.required) {
      const config = module.input.params[param];
      console.log(`  ${param}: ${config.description} (${config.type})`);
    }

    console.log('\n可选参数:');
    for (const param of module.input.optional) {
      const config = module.input.params[param];
      console.log(`  ${param}: ${config.description} (${config.type})`);
      if (config.default !== undefined) {
        console.log(`    默认值: ${config.default}`);
      }
    }

    console.log('\n输入格式:', module.input.accepts.join(', '));
    console.log('输出格式:', module.output.format);
  });

// 查看模块帮助
moduleCommand
  .command('help')
  .description('查看模块使用帮助')
  .argument('<name>', '模块名称')
  .action((name) => {
    const module = ModuleRegistry.get(name);

    if (!module) {
      console.error(`模块不存在: ${name}`);
      process.exit(1);
    }

    console.log(`\n使用方法:`);
    console.log(`  video-toolkit run --module ${name} [options]`);

    console.log(`\n示例:`);
    if (module.name === 'trim') {
      console.log(`  video-toolkit run --module trim --input input.mp4 --duration 60 --output trimmed.mp4`);
    }

    console.log(`\n参数说明:`);
    for (const [key, config] of Object.entries(module.input.params)) {
      const required = config.required ? '(必需)' : '(可选)';
      console.log(`  ${key}: ${config.description} ${required}`);
    }
  });
```

#### 3. `run` 命令 - 运行单个模块

```typescript
// src/cli/commands/run.ts
import { Command } from 'commander';
import { ModuleRegistry } from '../../modules';
import { FFmpegWrapper } from '../../utils/ffmpeg';
import { Logger } from '../../utils/logger';

export const runCommand = new Command('run')
  .description('运行单个模块')
  .requiredOption('-m, --module <name>', '模块名称')
  .option('-i, --input <file>', '输入文件')
  .option('-o, --output <file>', '输出文件')
  .allowUnknownOption(true)  // 允许传递模块特定参数
  .action(async (options) => {
    const module = ModuleRegistry.get(options.module);

    if (!module) {
      console.error(`模块不存在: ${options.module}`);
      console.error('使用 "video-toolkit module list" 查看可用模块');
      process.exit(1);
    }

    // 解析模块参数
    const params = parseModuleParams(options);

    // 构建执行上下文
    const ffmpeg = new FFmpegWrapper();
    const logger = new Logger(module.name);
    const context = {
      inputFile: options.input,
      outputFile: options.output,
      temporaryDir: '/tmp',
      log: (msg) => logger.info(msg),
      error: (msg) => logger.error(msg),
    };

    // 前置检查
    if (module.preCheck) {
      const ok = await module.preCheck(context);
      if (!ok) {
        console.error('前置检查失败');
        process.exit(1);
      }
    }

    // 执行模块
    logger.info(`执行模块: ${module.name}`);
    try {
      const outputFile = await module.execute(options.input, params, context);
      logger.success(`完成: ${outputFile}`);
    } catch (error) {
      logger.error(`执行失败: ${error.message}`);
      process.exit(1);
    }
  });

function parseModuleParams(options: any): any {
  const params: any = {};
  // 过滤掉 CLI 框架参数，保留模块参数
  for (const [key, value] of Object.entries(options)) {
    if (!['module', 'input', 'output'].includes(key)) {
      params[key] = value;
    }
  }
  return params;
}
```

#### 4. `create-workflow` 命令 - 创建自定义工作流

```typescript
// src/cli/commands/create-workflow.ts
import { Command } from 'commander';
import prompts from 'prompts';
import fs from 'fs/promises';
import path from 'path';

export const createWorkflowCommand = new Command('create-workflow')
  .description('创建自定义工作流')
  .option('-n, --name <name>', '工作流名称')
  .option('-d, --description <desc>', '工作流描述')
  .option('-o, --output <file>', '输出文件路径', 'workflow.json')
  .action(async (options) => {
    // 交互式询问
    const questions = [
      {
        type: 'text',
        name: 'name',
        message: '工作流名称:',
        initial: options.name || 'my-workflow',
      },
      {
        type: 'text',
        name: 'description',
        message: '工作流描述:',
        initial: options.description || '',
      },
      {
        type: 'confirm',
        name: 'addSteps',
        message: '现在添加处理步骤吗?',
        initial: true,
      },
    ];

    const answers = await prompts(questions);

    const steps = [];

    if (answers.addSteps) {
      let adding = true;
      while (adding) {
        const step = await addStep();
        steps.push(step);

        const { addAnother } = await prompts({
          type: 'confirm',
          name: 'addAnother',
          message: '继续添加步骤?',
          initial: false,
        });

        adding = addAnother;
      }
    }

    // 生成工作流配置
    const workflow = {
      name: answers.name,
      description: answers.description,
      version: '1.0.0',
      steps,
    };

    // 写入文件
    const outputPath = path.resolve(options.output);
    await fs.writeFile(outputPath, JSON.stringify(workflow, null, 2));

    console.log(`\n工作流已创建: ${outputPath}`);
    console.log(`使用方法: video-toolkit workflow ${answers.name}`);
  });

async function addStep(): Promise<any> {
  // 询问模块名称
  const { module } = await prompts({
    type: 'select',
    name: 'module',
    message: '选择模块:',
    choices: [
      { title: 'Trim - 裁剪时长', value: 'trim' },
      { title: 'Crop - 画面裁剪', value: 'crop' },
      { title: 'Compress - 压缩视频', value: 'compress' },
      { title: 'Normalize - 音频标准化', value: 'normalize' },
      { title: 'Watermark - 添加水印', value: 'watermark' },
    ],
  });

  const { name } = await prompts({
    type: 'text',
    name: 'name',
    message: '步骤名称 (可选):',
  });

  const { enabled } = await prompts({
    type: 'confirm',
    name: 'enabled',
    message: '启用此步骤?',
    initial: true,
  });

  return {
    module,
    name,
    enabled,
    params: {},  // 可以进一步询问参数
  };
}
```

### 用户体验设计

#### 命令示例

```bash
# 使用 YouTube 预设
video-toolkit workflow youtube \
  --input raw.mp4 \
  --output youtube-final.mp4

# 列出所有模块
video-toolkit module list

# 查看模块详情
video-toolkit module show trim

# 运行单个模块
video-toolkit run --module trim \
  --input video.mp4 \
  --duration 60 \
  --output trimmed.mp4

# 创建自定义工作流
video-toolkit create-workflow --name my-workflow

# 运行自定义工作流
video-toolkit workflow my-workflow \
  --input raw.mp4 \
  --output final.mp4

# 只验证不执行
video-toolkit workflow youtube --dry-run
```

#### 帮助输出

```bash
$ video-toolkit --help

Usage: video-toolkit [options] [command]

AI 原生视频处理工具箱

Options:
  -V, --version    输出版本号
  -h, --help       显示帮助信息

Commands:
  workflow [options] <name>     使用预设工作流处理视频
  module [options] [command]   模块管理
  run [options]                 运行单个模块
  create-workflow [options]     创建自定义工作流
  help [command]               显示命令帮助
```

---

## AI 原生接口设计

### 进化路径

#### MVP 阶段（当前）
```
video-toolkit workflow youtube --input raw.mp4 --output final.mp4
```
- 用户选择预设工作流
- 引擎组合模块执行

#### 第二阶段：模块级暴露
```
# 每个模块变成独立命令
video-toolkit crop --input raw.mp4 --width 1920 --height 1080 --output cropped.mp4
video-toolkit normalize --input cropped.mp4 --output normalized.mp4
video-toolkit compress --input normalized.mp4 --bitrate 8000k --output final.mp4
```
- AI 可以直接调用单个模块
- 支持灵活组合

#### 第三阶段：AI 原生接口
```
# AI 创建自定义工作流
video-toolkit create-workflow --config workflow.json
# workflow.json:
{
  "steps": [
    { "module": "crop", "params": { "width": 1920, "height": 1080 } },
    { "module": "normalize", "params": {} },
    { "module": "compress", "params": { "bitrate": "8000k" } }
  ]
}
```
- AI 直接生成工作流配置
- 完全可编程

### AI 优势

✅ **结构化接口**
- 每个模块有明确的输入/输出
- JSON 格式描述工作流
- AI 可以理解和组合模块

✅ **自描述能力**
- `--help` 自动发现所有模块
- 每个模块的能力清晰定义
- AI 可以动态学习新功能

✅ **可组合性**
- 模块可以任意组合
- AI 可以创建复杂工作流
- 无需硬编码预设

✅ **确定性输出**
- 每个步骤的输出可预测
- AI 可以验证每一步的结果
- 支持 TDD 风格的验证

---

## 依赖项（package.json）

```json
{
  "name": "video-toolkit",
  "version": "1.0.0",
  "description": "AI 原生视频处理工具箱",
  "main": "dist/index.js",
  "bin": {
    "video-toolkit": "./dist/cli/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "ts-node src/cli/index.ts",
    "test": "jest",
    "lint": "eslint src --ext .ts"
  },
  "dependencies": {
    "commander": "^12.0.0",
    "fluent-ffmpeg": "^2.1.2",
    "chalk": "^5.3.0",
    "prompts": "^2.4.2"
  },
  "devDependencies": {
    "@types/fluent-ffmpeg": "^2.1.24",
    "@types/node": "^20.10.0",
    "typescript": "^5.3.3",
    "jest": "^29.7.0",
    "@types/jest": "^29.5.11",
    "ts-jest": "^29.1.1"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

---

## 测试策略

### 单元测试

- **Workflow Engine**
  - Parser: JSON 解析、字段验证
  - Validator: 模块存在性、参数验证
  - Executor: 工作流执行、临时文件管理

- **Modules**
  - Trim: 参数验证、FFmpeg 命令生成
  - Crop: 参数计算、裁剪逻辑
  - Normalize: 音频处理、LUFS 标准化

### 端到端测试

- 完整工作流执行（YouTube、TikTok）
- 真实视频文件处理
- 输出文件验证

### 集成测试

- CLI 命令执行
- 模块注册和发现
- 工作流配置文件解析

---

## 发布计划

### 阶段 1：内测（1-2 个月）
- 10-20 核心用户
- 功能：基础工作流、5 个核心模块
- 反馈收集和快速迭代

### 阶段 2：公测（2-3 个月）
- 开放给早期用户
- 功能：批量处理、更多预设工作流
- 社区建设

### 阶段 3：正式发布（3-6 个月）
- Pro 版功能：批量处理、云存储集成
- 企业版功能：团队协作、API 集成
- 商业化启动

---

## 设计原则

- ✅ **模块化**: 每个模块独立，易于扩展
- ✅ **可组合**: 模块可以任意组合成工作流
- ✅ **结构化**: JSON 配置，AI 友好
- ✅ **确定性**: 每个步骤输出可预测
- ✅ **可测试**: 完整的测试覆盖
- ✅ **用户友好**: 清晰的 CLI 接口和帮助文档

---

*设计文档完成时间: 2026-03-16*
*设计批准状态: ✅ 已批准*
