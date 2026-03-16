// 工作流解析器
import fs from 'fs/promises';

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
