export type SectionType = 
  | '背景'
  | '人物介绍'
  | '为什么要读'
  | '核心观点'
  | '名词解释'
  | '整体总结'
  | '分段提纲'
  | '分段详述'
  | 'qa'
  | '金句'
  | '未总结内容'
  | '其他'
  | '原文双语版本（暂不支持）';

export interface ArticleSection {
  id: number;
  article_id: number;
  section_type: SectionType;
  content: string;
  sort_order: number;
}

export type ViewType = '精读' | '热闹' | '原文';

// 先定义所有小节类型
export const ALL_SECTION_TYPES: SectionType[] = [
  '背景',
  '人物介绍',
  '为什么要读',
  '核心观点',
  '名词解释',
  '整体总结',
  '分段提纲',
  '分段详述',
  'qa',
  '金句',
  '未总结内容',
  '其他',
  '原文双语版本（暂不支持）'
];

// 精读视图默认不选中的标签
export const DETAILED_EXCLUDED_SECTIONS = [
  '未总结内容',
  '其他',
  '原文双语版本（暂不支持）'
] as const;

// 视角预设配置
export const VIEW_CONFIGS = {
  精读: {
    includedSections: ALL_SECTION_TYPES
  },
  热闹: {
    includedSections: [
      '背景',
      '人物介绍',
      '为什么要读',
      '核心观点',
      '名词解释',
      '整体总结',
      '金句'
    ] as SectionType[]
  },
  原文: {
    includedSections: [
      '为什么要读',
      '核心观点',
      '分段提纲',
      'qa',
      '金句'
    ] as SectionType[]
  }
}; 