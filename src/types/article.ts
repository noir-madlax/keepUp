export interface Article {
  id: string;
  title: string;
  content: string;
  author: {
    name: string;
    avatar: string;
  };
  tags: string[];
  publishDate: string;
  coverImage: string;
  channel: string;
  originalLink: string; // 添加原文链接
}
