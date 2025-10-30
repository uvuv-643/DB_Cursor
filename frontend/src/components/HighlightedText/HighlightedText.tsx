import React from "react";
import { Tooltip } from "@gravity-ui/uikit";

export interface JsonMapping {
  [key: string]: string;
}

interface HighlightedTextProps {
  text: string;
  jsonMapping: JsonMapping;
  className?: string;
}

const HighlightedText: React.FC<HighlightedTextProps> = ({
  text,
  jsonMapping,
  className = "",
}) => {
  const pattern = Object.keys(jsonMapping)
    .map((key) => key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");

  const regex = new RegExp(`(${pattern})`, "gi");
  const parts = text.split(regex);

  const palette = [
    {
      bg: "rgba(33, 150, 243, 0.18)",
      hover: "rgba(33, 150, 243, 0.28)",
      border: "#2196F3",
    }, // blue
    {
      bg: "rgba(76, 175, 80, 0.18)",
      hover: "rgba(76, 175, 80, 0.28)",
      border: "#4CAF50",
    }, // green
    {
      bg: "rgba(255, 193, 7, 0.22)",
      hover: "rgba(255, 193, 7, 0.32)",
      border: "#FFC107",
    }, // amber
    {
      bg: "rgba(233, 30, 99, 0.18)",
      hover: "rgba(233, 30, 99, 0.28)",
      border: "#E91E63",
    }, // pink
    {
      bg: "rgba(156, 39, 176, 0.18)",
      hover: "rgba(156, 39, 176, 0.28)",
      border: "#9C27B0",
    }, // purple
    {
      bg: "rgba(0, 150, 136, 0.18)",
      hover: "rgba(0, 150, 136, 0.28)",
      border: "#009688",
    }, // teal
    {
      bg: "rgba(121, 85, 72, 0.18)",
      hover: "rgba(121, 85, 72, 0.28)",
      border: "#795548",
    }, // brown
    {
      bg: "rgba(96, 125, 139, 0.18)",
      hover: "rgba(96, 125, 139, 0.28)",
      border: "#607D8B",
    }, // blue grey
    {
      bg: "rgba(205, 220, 57, 0.22)",
      hover: "rgba(205, 220, 57, 0.32)",
      border: "#CDDC39",
    }, // lime
    {
      bg: "rgba(255, 152, 0, 0.22)",
      hover: "rgba(255, 152, 0, 0.32)",
      border: "#FF9800",
    }, // orange
  ];

  const tokenOrder = new Map<string, number>();
  let nextIndex = 0;

  return (
    <div className={className} style={{ lineHeight: 2, wordSpacing: 2 }}>
      {parts.map((part, index) => {
        const normalizedPart = part.toLowerCase();
        const isMatch = jsonMapping.hasOwnProperty(normalizedPart);

        if (isMatch) {
          if (!tokenOrder.has(normalizedPart)) {
            tokenOrder.set(normalizedPart, nextIndex++);
          }
          const colorIdx = tokenOrder.get(normalizedPart)! % palette.length;
          const scheme = palette[colorIdx];
          return (
            <Tooltip
              key={index}
              content={jsonMapping[normalizedPart]}
              placement="top"
              openDelay={300}
              closeDelay={100}
            >
              <span
                style={{
                  backgroundColor: scheme.bg,
                  border: `1px solid ${scheme.border}`,
                  cursor: "pointer",
                  padding: "1px 4px",
                  borderRadius: 4,
                  transition: "background-color 0.15s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = scheme.hover;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = scheme.bg;
                }}
              >
                {part}
              </span>
            </Tooltip>
          );
        }

        return <span key={index}>{part}</span>;
      })}
    </div>
  );
};

export default HighlightedText;
