import React from "react";
import styles from "./Funnel.module.css";
import { Text } from "@gravity-ui/uikit";
import { secondPartResults, thirdPartResults } from "../../requests/prompts";
import Trapezoid from "../../components/Trapezoid/Trapezoid";

export default function Funnel() {
  const pairs = React.useMemo(() => {
    const items = (
      secondPartResults || [
        "SELECT COUNT(*) FROM products WHERE product_weight_g > 500 AND product_length_cm < 30",
        "SELECT COUNT(*) FROM products WHERE product_weight_g > 500 AND product_length_cm < 30 AND product_height_cm > 15 AND product_width_cm < 20",
        "SELECT COUNT(*) FROM products JOIN product_category_name_translation ON products.product_category_name = product_category_name_translation.product_category_name WHERE product_weight_g > 500 AND product_length_cm < 30 AND product_height_cm > 15 AND product_width_cm < 20 AND product_photos_qty > 2 AND product_name_lenght > 10 AND product_description_lenght < 200 AND product_category_name_translation.product_category_name_english = 'electronics'",
      ]
    ).map((sql: string, i: number) => ({
      sql,
      count: (thirdPartResults || [515, 25, 10])[i] ?? 0,
      idx: i,
    }));
    const filtered = items.filter((x) => typeof x.count === "number");
    filtered.sort((a, b) => (b.count as number) - (a.count as number));
    return filtered.slice(0, 10);
  }, []);

  const [openIndex, setOpenIndex] = React.useState<number | null>(null);

  const maxCount = React.useMemo(
    () => pairs.reduce((m, x) => (x.count > m ? x.count : m), 1),
    [pairs]
  );

  const maxSize = 500; // px, for the largest disk
  const minSize = 40; // px, for the smallest disk

  const sizes = React.useMemo(() => {
    return pairs.map((stage) => {
      const ratio = maxCount > 0 ? stage.count / maxCount : 0;
      return Math.round(minSize + (maxSize - minSize) * ratio);
    });
  }, [pairs, maxCount]);

  const formatSql = (sql: string): string => {
    return sql
      .replace(/\bSELECT\b/gi, "\nSELECT")
      .replace(/\bFROM\b/gi, "\nFROM")
      .replace(/\bJOIN\b/gi, "\nJOIN")
      .replace(/\bWHERE\b/gi, "\nWHERE")
      .replace(/\bAND\b/gi, "\n  AND")
      .replace(/\bOR\b/gi, "\n  OR")
      .replace(/\bON\b/gi, "\n  ON")
      .trim();
  };

  const selectedStage = openIndex !== null ? pairs[openIndex] : null;

  return (
    <div className={styles.container}>
      <Text variant="header-2">Воронка</Text>
      <Text>Клики по дискам показывают SQL запрос.</Text>

      <div className={styles.contentWrapper}>
        <div className={styles.funnelWrapper}>
          <div className={styles.stageList}>
            {pairs.map((stage, i) => {
              return (
                <div
                  key={i}
                  className={styles.stage}
                  style={{ zIndex: 100 - i }}
                >
                  <div
                    className={styles.disk}
                    onClick={() => setOpenIndex((v) => (v === i ? null : i))}
                    style={{
                      width: sizes[i],
                      backgroundColor: "var(--g-color-base-brand)",
                      height: 30,
                      borderRadius: "50%",
                      opacity: openIndex === i ? 1 : 0.7,
                    }}
                  >
                    <Text variant="body-2">{stage.count}</Text>
                  </div>
                  {i < pairs.length - 1 && (
                    <div className={styles.connector}>
                      <Trapezoid
                        topWidth={sizes[i]}
                        bottomWidth={sizes[i + 1]}
                        height={60}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {selectedStage && (
          <div className={styles.sqlPanel}>
            <div
              style={{
                fontSize: 12,
                opacity: 0.8,
                marginBottom: 6,
                letterSpacing: 0.2,
              }}
            >
              SQL
            </div>
            <pre
              style={{
                margin: 0,
                whiteSpace: "pre-wrap",
                lineHeight: 1.5,
                fontSize: 12.5,
                wordBreak: "break-word",
              }}
            >
              {formatSql(selectedStage.sql)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
