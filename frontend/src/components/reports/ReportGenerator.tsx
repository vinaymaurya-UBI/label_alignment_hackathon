import { Button, Stack, LinearProgress, Typography } from "@mui/material";
import { useState } from "react";
import useReportStream from "../../hooks/useReportStream";

interface Props {
  drugId: number;
  onReport: (markdown: string) => void;
}

function ReportGenerator({ drugId, onReport }: Props) {
  const [started, setStarted] = useState(false);
  const { start, status, progress } = useReportStream({
    drugId,
    onComplete: onReport
  });

  const handleClick = () => {
    setStarted(true);
    start();
  };

  return (
    <Stack spacing={2}>
      <Button variant="contained" onClick={handleClick} disabled={started && status === "starting"}>
        Generate AI Report
      </Button>
      {started && (
        <Stack spacing={1}>
          <Typography variant="body2">Status: {status}</Typography>
          <LinearProgress variant={progress !== undefined ? "determinate" : "indeterminate"} value={progress ?? 0} />
        </Stack>
      )}
    </Stack>
  );
}

export default ReportGenerator;

