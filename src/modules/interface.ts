// 模块接口定义
export interface VideoModule {
  name: string;
  description: string;
  version: string;
  category: 'video' | 'audio' | 'core';
  input: {
    accepts: string[];
    required: string[];
    optional: string[];
    params: {
      [key: string]: {
        type: 'string' | 'number' | 'boolean' | 'file' | 'enum';
        description: string;
        enum?: string[];
        default?: any;
        required?: boolean;
      };
    };
  };
  output: {
    format: string;
    filename: string;
    metadata?: { [key: string]: string | number };
  };
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
