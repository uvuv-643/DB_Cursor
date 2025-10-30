import { getApiBaseUrl } from "./global";

export type ConnectionCredentials = {
  host: string;
  port: string | number;
  database: string;
  username: string;
  password: string;
};

export type ConnectionTokenResponse = {
  token_id?: string;
  tokenId?: string;
  [key: string]: unknown;
};

export async function createConnectionToken(
  credentials: ConnectionCredentials
): Promise<ConnectionTokenResponse> {
  const apiBase = getApiBaseUrl();
  const url = `${apiBase}/connections/`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      host: credentials.host,
      port: String(credentials.port),
      database: credentials.database,
      username: credentials.username,
      password: credentials.password,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed: ${response.status} ${text}`);
  }

  return (await response.json()) as ConnectionTokenResponse;
}
