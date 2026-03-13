import { useState } from "react";

interface Options {
  drugId: string;
  onComplete: (markdown: string) => void;
}

interface State {
  status: "idle" | "starting" | "generating" | "complete" | "error";
  progress: number;
  message: string;
  error: string | null;
}

function useReportStream({ drugId, onComplete }: Options) {
  const [state, setState] = useState<State>({
    status: "idle",
    progress: 0,
    message: "",
    error: null,
  });

  const start = async () => {
    setState({ status: "starting", progress: 0, message: "Initializing...", error: null });

    const base = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const url = `${base}/api/v1/ai/generate-report/${drugId}`;

    try {
      const response = await fetch(url, { method: "POST" });
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.status === "complete") {
              setState({ status: "complete", progress: 100, message: data.message ?? "Done", error: null });
              onComplete(data.report ?? "");
            } else if (data.status === "error") {
              setState({ status: "error", progress: 0, message: "", error: data.message ?? "Unknown error" });
            } else {
              setState({ status: data.status, progress: data.progress ?? 0, message: data.message ?? "", error: null });
            }
          } catch {
            // ignore malformed SSE lines
          }
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Network error";
      setState({ status: "error", progress: 0, message: "", error: msg });
    }
  };

  return { ...state, start };
}

export default useReportStream;
