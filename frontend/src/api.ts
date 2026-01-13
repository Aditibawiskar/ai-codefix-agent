import axios from "axios";
import type { CodeFixRequest, CodeFixResponse } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export async function fixCode(payload: CodeFixRequest): Promise<CodeFixResponse> {
  const resp = await axios.post<CodeFixResponse>(`${API_BASE_URL}/fix`, payload);
  return resp.data;
}
