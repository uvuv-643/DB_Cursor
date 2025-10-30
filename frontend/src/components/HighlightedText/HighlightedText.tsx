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

  return (
    <div className={className}>
      {parts.map((part, index) => {
        const normalizedPart = part.toLowerCase();
        const isMatch = jsonMapping.hasOwnProperty(normalizedPart);

        if (isMatch) {
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
                  backgroundColor: "#ffeb3b",
                  cursor: "pointer",
                  padding: "2px 4px",
                  borderRadius: "3px",
                  transition: "background-color 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "#ffd54f";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "#ffeb3b";
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
