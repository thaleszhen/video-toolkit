// 模块注册表
import { VideoModule } from './interface';
import { trimModule } from './core/trim';
import { cropModule } from './core/crop';
import { compressModule } from './core/compress';
import { watermarkModule } from './core/watermark';
import { normalizeModule } from './core/normalize';

const moduleRegistry: Map<string, VideoModule> = new Map();

// 注册核心模块
moduleRegistry.set(trimModule.name, trimModule);
moduleRegistry.set(cropModule.name, cropModule);
moduleRegistry.set(compressModule.name, compressModule);
moduleRegistry.set(watermarkModule.name, watermarkModule);
moduleRegistry.set(normalizeModule.name, normalizeModule);

export class ModuleRegistry {
  static register(module: VideoModule) {
    moduleRegistry.set(module.name, module);
  }

  static get(name: string): VideoModule | undefined {
    return moduleRegistry.get(name);
  }

  static getAll(): VideoModule[] {
    return Array.from(moduleRegistry.values());
  }

  static listByCategory(category: string): VideoModule[] {
    return this.getAll().filter(m => m.category === category);
  }

  // 内部方法，用于测试清空注册表
  static _clear() {
    moduleRegistry.clear();
  }
}
