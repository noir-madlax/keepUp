export interface Article {
  id: number;
  title: string;
  content: string;
  author_id: number;
  author?: {
    id: number;
    name: string;
    icon?: string;
  };
  channel: string;
  created_at: string;
  tags: string[];
  publish_date: string | null;
  original_link: string | null;
  user_id: string | null;
}
