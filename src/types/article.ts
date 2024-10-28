export interface Article {
  id: string;
  title: string;
  content: string;
  summary: string;
  author: {
    name: string;
    avatar: string;
  };
  tags: string[];
  publishDate: string;
  coverImage: string;
}
