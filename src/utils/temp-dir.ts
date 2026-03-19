import * as fs from 'fs/promises';
import path from 'path';

export type TempScope = 'run' | 'workflow' | 'inputs';

export async function createManagedTempDir(scope: TempScope, rootDir: string = process.cwd()) {
  const baseDir = path.join(rootDir, 'tmp', scope);
  await fs.mkdir(baseDir, { recursive: true });
  return fs.mkdtemp(path.join(baseDir, `${scope}-`));
}
