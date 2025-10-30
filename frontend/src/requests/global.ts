export function getApiBaseUrl(): string {
  const base = "https://api.uvuv643.ru";
  return base?.replace(/\/$/, "") || "";
}
