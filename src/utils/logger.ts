// 日志工具
export class Logger {
  private context: string;

  constructor(context: string) {
    this.context = context;
  }

  info(message: string) {
    console.log(`[${this.context}]`, message);
  }

  warn(message: string) {
    console.warn(`[${this.context}]`, message);
  }

  error(message: string) {
    console.error(`[${this.context}]`, message);
  }

  success(message: string) {
    console.log(`[${this.context}]`, message);
  }
}
