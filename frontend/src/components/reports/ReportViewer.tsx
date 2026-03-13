interface Props {
  markdown: string;
}

function ReportViewer({ markdown }: Props) {
  // Simple preformatted block; you can enhance with marked.js if desired
  return (
    <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
      {markdown}
    </pre>
  );
}

export default ReportViewer;

