import { getApiBaseUrl } from "./global";

export type SendPromptRequest = {
  query: string;
};

export type SendPromptResponse = unknown;

export async function sendPrompt(
  params: SendPromptRequest
): Promise<SendPromptResponse> {
  const apiBase = getApiBaseUrl();
  const url = `${apiBase}/prompts/`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt: params.query }),
    credentials: "include",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed: ${response.status} ${text}`);
  }

  return (await response.json()) as SendPromptResponse;
}
