import { useState, useEffect } from "react";

export function useAnimatedNumber(targetValue: number, durationMs: number = 500) {
  const [currentValue, setCurrentValue] = useState(targetValue);

  useEffect(() => {
    if (currentValue === targetValue) return;

    let startTimestamp: number;
    const startValue = currentValue;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / durationMs, 1);
      
      // Easing function (easeOutQuad)
      const easeProgress = progress * (2 - progress);
      
      setCurrentValue(Math.floor(startValue + (targetValue - startValue) * easeProgress));

      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        setCurrentValue(targetValue);
      }
    };

    window.requestAnimationFrame(step);
  }, [targetValue, durationMs]);

  return currentValue;
}
