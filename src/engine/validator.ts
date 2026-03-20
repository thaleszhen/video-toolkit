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

    const mergedParams = this.applyDefaults(step.params || {}, module.input.params);

    for (const requiredParam of module.input.required) {
      if (!this.hasValue(mergedParams[requiredParam])) {
        errors.push({
          step: index,
          module: step.module,
          error: `Missing required parameter: ${requiredParam}`,
        });
      }
    }

    if (errors.length === 0 && module.validate && !module.validate(mergedParams)) {
      errors.push({
        step: index,
        module: step.module,
        error: 'Module parameter validation failed',
      });
    }

    return errors;
  }

  private static hasValue(value: unknown): boolean {
    return value !== undefined && value !== null && value !== '';
  }

  private static applyDefaults(
    params: Record<string, any>,
    definitions: Record<string, { default?: any }>
  ): Record<string, any> {
    const merged = { ...params };

    for (const [key, definition] of Object.entries(definitions)) {
      if (merged[key] === undefined && definition.default !== undefined) {
        merged[key] = definition.default;
      }
    }

    return merged;
  }
}
