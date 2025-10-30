import React from "react";
import styles from "./Funnel.module.css";
import { Text } from "@gravity-ui/uikit";

export default function Funnel() {
  return (
    <div className={styles.container}>
      <Text variant="header-2">Воронка</Text>
      <Text>Здесь будет следующий этап построения сегментации.</Text>
    </div>
  );
}
