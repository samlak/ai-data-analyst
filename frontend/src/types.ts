export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  loading?: boolean;
  error?: boolean;
  tableOutput?: boolean;
  imageUrl?: string;
  analysis?: string;
}

export interface ApiResponse {
  table_output_verified: boolean;
  execution_result: string;
  image_url: string | null;
  analysis: string | null;
}