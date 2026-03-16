// 模块注册表
import { VideoModule } from './interface';

const moduleRegistry: Map<string, VideoModule> = new Map();

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
