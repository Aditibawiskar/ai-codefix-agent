export interface CodeDiff {
  filepath: string;
  diff: string;
}

export interface TokenUsage {
  total_tokens?: number;
  [key: string]: number | undefined;
}

export interface CodeFixResponse {
  diffs: CodeDiff[];
  test_stub: string;
  explanation: string;
  model_used: string;
  token_usage?: TokenUsage | null;
}

export interface CodeFixRequest {
  code: string;
  file_path?: string | null;
}
