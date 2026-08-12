import { useEffect, useState } from "react";

/** Cycles through a list of "thinking" lines on an interval — a static message otherwise. */
export function useCyclingMessage(message: string | string[], intervalMs = 1600) {
  const messages = Array.isArray(message) ? message : [message];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
    if (messages.length <= 1) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % messages.length);
    }, intervalMs);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [Array.isArray(message) ? message.join("|") : message]);

  return messages[index]!;
}
