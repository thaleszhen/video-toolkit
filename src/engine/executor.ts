// 工作流执行器
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

    const temporaryDir = await fs.mkdtemp(path.join(process.cwd(), 'temp-'));
    this.temporaryFiles.push(temporaryDir);

    let currentInput = inputFile;
    let stepsCompleted = 0;

    for (let i = 0; i < this.config.steps.length; i++) {
      const step = this.config.steps[i];

      if (step.enabled === false) {
        this.logger.info(`Skipping disabled step: ${step.module}`);
        continue;
      }

      const module = ModuleRegistry.get(step.module);
      if (!module) {
        throw new Error(`Module not found: ${step.module}`);
      }

      const isLastStep = i === this.config.steps.length - 1;
      const stepOutputFile = isLastStep
        ? outputFile
        : path.join(temporaryDir, `${step.module}-${i}-${path.basename(inputFile)}`);

      const context: ExecutionContext = {
        inputFile: currentInput,
        outputFile: stepOutputFile,
        workingDir: temporaryDir,
        temporaryDir,
        log: (message: string) => this.logger.info(message),
        error: (message: string) => this.logger.error(message),
      };

      if (module.preCheck) {
        const ok = await module.preCheck(context);
        if (!ok) {
          throw new Error(`Pre-check failed for module: ${step.module}`);
        }
      }

      this.logger.info(`Executing step ${i + 1}/${this.config.steps.length}: ${step.module}`);
      await module.execute(currentInput, step.params, context);

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
