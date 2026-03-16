// 工作流验证器
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

    const module = ModuleRegistry.get(step.module);
    if (!module) {
      errors.push({
        step: index,
        module: step.module,
        error: `Module '${step.module}' not found`,
      });
      return errors;
    }

    for (const requiredParam of module.input.required) {
      if (!step.params[requiredParam]) {
        errors.push({
          step: index,
          module: step.module,
          error: `Missing required parameter: ${requiredParam}`,
        });
      }
    }

    return errors;
  }
}
