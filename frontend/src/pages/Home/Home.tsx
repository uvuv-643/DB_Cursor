import React from "react";
import styles from "./Home.module.css";

import { Button, Text, TextInput, useToaster } from "@gravity-ui/uikit";
import { createConnectionToken } from "../../requests/connections";
import { useNavigate } from "react-router";
import { sleep } from "../../utils/utils";

export default function Home() {
  const [host, setHost] = React.useState("");
  const [port, setPort] = React.useState("5432");
  const [database, setDatabase] = React.useState("");
  const [user, setUser] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
  }

  const navigate = useNavigate();

  const { add } = useToaster();

  async function onConnectClick() {
    setError(null);
    setLoading(true);
    try {
      await createConnectionToken({
        host,
        port,
        database,
        username: user,
        password,
      });
      add({
        name: "connection-success",
        title: "Подключение успешно",
        theme: "success",
      });
      await sleep(1000);
      navigate("/prompt");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.appContainer}>
      <div className={styles.imageContainer}>
        <img src="/meme2.webp" alt="" />
      </div>
      <div className={styles.contentContainer}>
        <div className={styles.container}>
          <Text variant="header-2">
            Построение сегментов на основе описания от человека
          </Text>
          <Text>Для начала работы подключитесь к базе данных:</Text>
          <form className={styles.form} onSubmit={onSubmit}>
            <div className={styles.row}>
              <Text>Хост</Text>
              <TextInput
                value={host}
                onUpdate={setHost}
                placeholder="localhost"
              />
            </div>
            <div className={styles.row}>
              <Text>Порт</Text>
              <TextInput value={port} onUpdate={setPort} placeholder="5432" />
            </div>
            <div className={styles.row}>
              <Text>Название БД</Text>
              <TextInput
                value={database}
                onUpdate={setDatabase}
                placeholder="postgres"
              />
            </div>
            <div className={styles.row}>
              <Text>Пользователь</Text>
              <TextInput
                value={user}
                onUpdate={setUser}
                placeholder="postgres"
              />
            </div>
            <div className={styles.row}>
              <Text>Пароль</Text>
              <TextInput
                value={password}
                placeholder="Мы не храним данные и все взаимодействия с БД идут напрямую"
                onUpdate={setPassword}
                type="password"
              />
            </div>
          </form>
          <Button
            view="action"
            size="m"
            loading={loading}
            onClick={onConnectClick}
          >
            Подключиться
          </Button>
          {error ? <Text color="danger">{error}</Text> : null}
        </div>
      </div>
    </div>
  );
}
