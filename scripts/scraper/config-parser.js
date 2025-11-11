import fs from 'fs';
import path from 'path';
import YAML from 'yaml';

/**
 * 加载YAML配置文件
 */
export function loadConfig(configPath) {
  const fullPath = path.resolve(configPath);
  
  if (!fs.existsSync(fullPath)) {
    throw new Error(`配置文件不存在: ${fullPath}`);
  }

  const content = fs.readFileSync(fullPath, 'utf8');
  const config = YAML.parse(content);

  if (!config) {
    throw new Error('配置文件解析失败');
  }

  return config;
}

/**
 * 验证配置完整性
 */
export function validateConfig(config) {
  const required = ['url', 'name', 'steps'];
  const missing = required.filter(field => !config[field]);

  if (missing.length > 0) {
    throw new Error(`配置缺少必需字段: ${missing.join(', ')}`);
  }

  if (!Array.isArray(config.steps) || config.steps.length === 0) {
    throw new Error('配置必须包含至少一个步骤');
  }

  return true;
}

