import * as fs from 'fs/promises';
import path from 'path';
import youtubedl from 'youtube-dl-exec';
import { createManagedTempDir } from './temp-dir';

const YOUTUBE_HOSTS = new Set([
  'youtube.com',
  'www.youtube.com',
  'm.youtube.com',
  'music.youtube.com',
  'youtu.be',
  'www.youtu.be',
]);

const VIDEO_EXTENSIONS = new Set(['.mp4', '.mov', '.mkv', '.webm', '.m4v']);

export interface ResolveInputSourceOptions {
  workingDir?: string;
  log?: (message: string) => void;
  keepDownloadedSource?: boolean;
  downloadDir?: string;
}

export interface ResolvedInputSource {
  originalInput: string;
  resolvedInput: string;
  baseName: string;
  downloaded: boolean;
  cleanup: () => Promise<void>;
}

function isFileProtocolUrl(input: string): boolean {
  try {
    const parsed = new URL(input);
    return parsed.protocol === 'file:';
  } catch {
    return false;
  }
}

export function isHttpUrl(input: string): boolean {
  try {
    const parsed = new URL(input);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

export function isYouTubeUrl(input: string): boolean {
  if (!isHttpUrl(input)) {
    return false;
  }

  const parsed = new URL(input);
  return YOUTUBE_HOSTS.has(parsed.hostname.toLowerCase());
}

export function extractYouTubeVideoId(input: string): string | undefined {
  if (!isYouTubeUrl(input)) {
    return undefined;
  }

  const parsed = new URL(input);
  const host = parsed.hostname.toLowerCase();

  if (host.includes('youtu.be')) {
    const segments = parsed.pathname.split('/').filter(Boolean);
    return segments[0] || undefined;
  }

  const queryVideoId = parsed.searchParams.get('v');
  if (queryVideoId) {
    return queryVideoId;
  }

  const segments = parsed.pathname.split('/').filter(Boolean);
  const markerIndex = segments.findIndex(segment =>
    ['shorts', 'live', 'embed', 'watch'].includes(segment)
  );

  if (markerIndex >= 0 && segments[markerIndex + 1]) {
    return segments[markerIndex + 1];
  }

  return undefined;
}

export function sanitizeFileBaseName(raw: string): string {
  const sanitized = raw
    .trim()
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');

  return sanitized || 'video-input';
}

async function ensureLocalInputExists(input: string): Promise<void> {
  try {
    await fs.access(input);
  } catch {
    throw new Error(`输入文件不存在: ${input}`);
  }
}

async function pickDownloadedVideoFile(downloadDir: string, expectedBaseName: string): Promise<string> {
  const entries = await fs.readdir(downloadDir, { withFileTypes: true });
  const files = await Promise.all(
    entries
      .filter(entry => entry.isFile())
      .map(async entry => {
        const fullPath = path.join(downloadDir, entry.name);
        const stat = await fs.stat(fullPath);
        return {
          name: entry.name,
          fullPath,
          size: stat.size,
          extension: path.extname(entry.name).toLowerCase(),
        };
      })
  );

  const videoFiles = files.filter(file => VIDEO_EXTENSIONS.has(file.extension));
  if (videoFiles.length === 0) {
    throw new Error('下载完成，但未找到可用的视频文件');
  }

  const preferredName = `${expectedBaseName}.mp4`.toLowerCase();
  const preferred = videoFiles.find(file => file.name.toLowerCase() === preferredName);
  if (preferred) {
    return preferred.fullPath;
  }

  const withoutFormatSuffix = videoFiles.filter(file => !/\.f\d+\./i.test(file.name));
  const candidates = withoutFormatSuffix.length > 0 ? withoutFormatSuffix : videoFiles;
  candidates.sort((a, b) => b.size - a.size);

  return candidates[0].fullPath;
}

async function downloadYouTubeInput(
  input: string,
  workingDir: string,
  options: ResolveInputSourceOptions = {}
): Promise<ResolvedInputSource> {
  const keepDownloadedSource = options.keepDownloadedSource || Boolean(options.downloadDir);
  const videoId = extractYouTubeVideoId(input);
  const baseName = sanitizeFileBaseName(videoId ? `youtube-${videoId}` : 'youtube-video');
  const persistentDir = options.downloadDir
    ? path.resolve(workingDir, options.downloadDir)
    : path.join(workingDir, 'downloads', 'youtube');
  const downloadDir = keepDownloadedSource
    ? persistentDir
    : await createManagedTempDir('inputs', workingDir);
  const outputTemplate = path.join(downloadDir, `${baseName}.%(ext)s`);

  if (keepDownloadedSource) {
    await fs.mkdir(downloadDir, { recursive: true });
  }

  try {
    options.log?.(`检测到 YouTube 链接，正在下载: ${input}`);
    await youtubedl(input, {
      output: outputTemplate,
      format: 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
      mergeOutputFormat: 'mp4',
      noPlaylist: true,
      restrictFilenames: true,
    });

    const resolvedInput = await pickDownloadedVideoFile(downloadDir, baseName);
    options.log?.(`下载完成，使用文件: ${resolvedInput}`);

    return {
      originalInput: input,
      resolvedInput,
      baseName: sanitizeFileBaseName(path.basename(resolvedInput, path.extname(resolvedInput))),
      downloaded: true,
      cleanup: async () => {
        if (!keepDownloadedSource) {
          await fs.rm(downloadDir, { recursive: true, force: true });
        }
      },
    };
  } catch (error: any) {
    if (!keepDownloadedSource) {
      await fs.rm(downloadDir, { recursive: true, force: true });
    }
    throw new Error(`YouTube 下载失败: ${error?.stderr || error?.message || String(error)}`);
  }
}

export async function resolveInputSource(
  input: string,
  options: ResolveInputSourceOptions = {}
): Promise<ResolvedInputSource> {
  const normalizedInput = input.trim();
  const workingDir = options.workingDir || process.cwd();
  const cleanup = async () => {};

  if (isYouTubeUrl(normalizedInput)) {
    return downloadYouTubeInput(normalizedInput, workingDir, options);
  }

  if (isHttpUrl(normalizedInput) || isFileProtocolUrl(normalizedInput)) {
    const parsed = new URL(normalizedInput);
    const inferredName = sanitizeFileBaseName(path.basename(parsed.pathname || 'remote-input'));
    return {
      originalInput: input,
      resolvedInput: normalizedInput,
      baseName: inferredName,
      downloaded: false,
      cleanup,
    };
  }

  await ensureLocalInputExists(normalizedInput);
  return {
    originalInput: input,
    resolvedInput: normalizedInput,
    baseName: sanitizeFileBaseName(path.basename(normalizedInput, path.extname(normalizedInput))),
    downloaded: false,
    cleanup,
  };
}
