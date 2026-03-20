import fs from 'fs/promises';
import path from 'path';

export const BUILT_IN_WORKFLOWS = ['youtube', 'tiktok'] as const;

export interface ResolveWorkflowConfigOptions {
  name?: string;
  configPath?: string;
  workingDir?: string;
}

async function pathExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

function uniquePaths(paths: string[]): string[] {
  return Array.from(new Set(paths));
}

function buildPresetCandidates(name: string, workingDir: string): string[] {
  const fileName = name.endsWith('.json') ? name : `${name}.json`;
  const looksLikePath = fileName.includes(path.sep) || fileName.includes('/') || fileName.includes('\\');
  const explicitPath = path.resolve(workingDir, fileName);

  return uniquePaths([
    ...(looksLikePath ? [explicitPath] : []),
    path.resolve(workingDir, 'src', 'presets', fileName),
    path.resolve(__dirname, '..', 'presets', fileName),
    path.resolve(__dirname, '..', '..', 'src', 'presets', fileName),
  ]);
}

export async function resolveWorkflowConfigPath(
  options: ResolveWorkflowConfigOptions = {}
): Promise<string> {
  const workingDir = options.workingDir || process.cwd();

  if (options.configPath) {
    const resolvedConfig = path.resolve(workingDir, options.configPath);
    if (await pathExists(resolvedConfig)) {
      return resolvedConfig;
    }

    throw new Error(`未找到工作流配置文件: ${resolvedConfig}`);
  }

  if (!options.name) {
    throw new Error('请提供工作流名称或 --config <file>');
  }

  const candidates = buildPresetCandidates(options.name, workingDir);
  for (const candidate of candidates) {
    if (await pathExists(candidate)) {
      return candidate;
    }
  }

  throw new Error(
    `未找到工作流配置: ${options.name}。可用预设: ${BUILT_IN_WORKFLOWS.join(', ')}，或使用 --config <file>`
  );
}

export function buildBatchOutputPath(inputFile: string, outputDir: string, workflowName: string): string {
  const baseName = path.basename(inputFile, path.extname(inputFile));
  return path.join(path.resolve(outputDir), `${baseName}-${workflowName}.mp4`);
}
