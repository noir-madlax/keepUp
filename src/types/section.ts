import { useI18n } from 'vue-i18n'

export type SectionType = 
  | '总结'
  | '人物介绍'
  | '名词解释'
  | '分段提纲'
  | 'QA环节'
  | '金句'
  | '引用（测试）'
  | '结构图（测试）'
  | '案例（测试）'
  | '原文字幕（测试）'
  | '翻译字幕（测试）'
  | '彩蛋（测试）';

export interface ArticleSection {
  id: number;
  article_id: number;
  section_type: SectionType;
  content: string;
  sort_order: number;
}

export type ViewType = '默认视图';

// 先定义所有小节类型（确保总结在最前面）
export const ALL_SECTION_TYPES: SectionType[] = [
  '总结',
  '人物介绍',
  '名词解释',
  '分段提纲',
  'QA环节',
  '金句',
  '引用（测试）',
  '结构图（测试）',
  '案例（测试）',
  '原文字幕（测试）',
  '翻译字幕（测试）',
  '彩蛋（测试）'
];

// 默认选中的小节（确保总结在最前面）
export const DEFAULT_SELECTED_SECTIONS: SectionType[] = [
  '总结',
  '人物介绍',
  '名词解释',
  '分段提纲',
  'QA环节',
  '金句'
];

// 视角预设配置
export const VIEW_CONFIGS = {
  默认视图: {
    includedSections: DEFAULT_SELECTED_SECTIONS
  }
};

// 添加一个函数来获取本地化的小节类型显示文本
export const getLocalizedSectionType = (type: SectionType): string => {
  const { t, locale } = useI18n()
  
  // 如果是英文环境,使用翻译
  if (locale.value === 'en') {
    return t(`article.sections.types.${type}`)
  }
  // 中文环境直接返回原始类型
  return type
}

// 添加一个函数来获取本地化的所有小节类型
export const getLocalizedSectionTypes = (): string[] => {
  return ALL_SECTION_TYPES.map(type => getLocalizedSectionType(type))
} 