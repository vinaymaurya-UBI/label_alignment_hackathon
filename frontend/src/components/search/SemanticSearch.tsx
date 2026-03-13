import { useState } from "react";
import { TextField, Button, Stack, Typography, Card, CardContent } from "@mui/material";
import { useSemanticSearch } from "../../hooks/useSemanticSearch";

function SemanticSearch() {
  const [query, setQuery] = useState("");
  const { data, isLoading, error, search } = useSemanticSearch();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    search(query);
  };

  return (
    <Stack spacing={2}>
      <form onSubmit={handleSubmit}>
        <Stack direction="row" spacing={2}>
          <TextField
            fullWidth
            label="Semantic search query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Button type="submit" variant="contained">
            Search
          </Button>
        </Stack>
      </form>

      {isLoading && <Typography>Searching...</Typography>}
      {error && <Typography color="error">Search failed.</Typography>}

      {data && data.length > 0 && (
        <Stack spacing={2}>
          {data.map((item) => (
            <Card key={item.section_id}>
              <CardContent>
                <Typography variant="subtitle2">
                  {item.heading} ({item.country_code})
                </Typography>
                <Typography variant="body2">{item.content.slice(0, 300)}...</Typography>
              </CardContent>
            </Card>
          ))}
        </Stack>
      )}
    </Stack>
  );
}

export default SemanticSearch;

