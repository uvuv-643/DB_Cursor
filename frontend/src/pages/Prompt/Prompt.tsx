import React from "react";
import styles from "./Prompt.module.css";

import { Button, Text, TextArea } from "@gravity-ui/uikit";
import { sendPrompt } from "../../requests/prompts";
import HighlightedText, {
  JsonMapping,
} from "../../components/HighlightedText/HighlightedText";

export default function Prompt() {
  const [query, setQuery] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<unknown>(null);
  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
  }
  const onConnectClick = async () => {
    setLoading(true);
    try {
      setError(null);
      const data = await sendPrompt({
        query,
      });
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.appContainer}>
      <div className={styles.imageContainer}>
        <img src="/meme.jpg" alt="" />
      </div>
      <div className={styles.contentContainer}>
        <div className={styles.container}>
          <Text variant="header-2">
            Построение сегментов на основе описания от человека
          </Text>
          <Text>Введите Ваш запрос к базе данных: </Text>
          <form className={styles.form} onSubmit={onSubmit}>
            <div className={styles.row}>
              <Text>Запрос</Text>
              <TextArea
                value={query}
                rows={7}
                onUpdate={setQuery}
                placeholder="Опишите детально то, что хотите получить из базы данных"
              />
            </div>
            <Button
              view="action"
              size="m"
              loading={loading}
              onClick={onConnectClick}
            >
              Отправить
            </Button>
          </form>
          {error ? <Text color="danger">{error}</Text> : null}
          {result ? (
            <HighlightedText text={query} jsonMapping={result as JsonMapping} />
          ) : null}
        </div>
      </div>
    </div>
  );
}
