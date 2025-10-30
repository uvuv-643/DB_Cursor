const Trapezoid = ({
  topWidth = 200,
  bottomWidth = 100,
  height = 80,
  color = "var(--g-color-base-brand)",
  strokeWidth = 2,
  className = "",
}) => {
  // Рассчитываем координаты для точек трапеции
  const horizontalOffset = (topWidth - bottomWidth) / 2;

  // Компенсируем толщину линии для визуального выравнивания
  const compensation = strokeWidth / 2;

  // Рассчитываем угол наклона для компенсации
  const leftSlope = Math.atan2(height, horizontalOffset);
  const rightSlope = Math.atan2(height, horizontalOffset);

  const topLeft = [compensation, compensation];
  const topRight = [topWidth - compensation, compensation];
  const bottomLeft = [
    horizontalOffset + Math.sin(leftSlope) * compensation,
    height - Math.cos(leftSlope) * compensation,
  ];
  const bottomRight = [
    horizontalOffset + bottomWidth - Math.sin(rightSlope) * compensation,
    height - Math.cos(rightSlope) * compensation,
  ];

  return (
    <svg
      width={topWidth}
      height={height}
      viewBox={`0 0 ${topWidth} ${height}`}
      className={className}
    >
      {/* Левая боковая грань */}
      <line
        x1={topLeft[0]}
        y1={topLeft[1]}
        x2={bottomLeft[0]}
        y2={bottomLeft[1]}
        stroke={color}
        strokeWidth={strokeWidth}
      />

      {/* Правая боковая грань */}
      <line
        x1={topRight[0]}
        y1={topRight[1]}
        x2={bottomRight[0]}
        y2={bottomRight[1]}
        stroke={color}
        strokeWidth={strokeWidth}
      />
    </svg>
  );
};

export default Trapezoid;
