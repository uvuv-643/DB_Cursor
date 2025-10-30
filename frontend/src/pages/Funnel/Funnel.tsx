import React from "react";
import styles from "./Funnel.module.css";
import { Text } from "@gravity-ui/uikit";
import { secondPartResults, thirdPartResults } from "../../requests/prompts";

export default function Funnel() {
  return (
    <div className={styles.container}>
      <Text variant="header-2">Воронка</Text>
      <Text>Здесь будет следующий этап построения сегментации.</Text>

      {thirdPartResults.map((result, index) => (
        <Text key={index}>
          {secondPartResults[index]} - {result}
        </Text>
      ))}
    </div>
  );
}
