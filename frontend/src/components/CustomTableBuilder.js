import React, { useState, useEffect } from 'react'; // Added useEffect
import {
  Box, Button, Typography, Paper,
  Select, MenuItem, Chip, Grid, FormControl, InputLabel, // Added FormControl, InputLabel
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow // Added Table components
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material'; // Added icons

// Placeholder: Assume document data structure includes extracted fields/columns
// Example: document.financial_data.metrics, document.tables[page_num][table_index].header etc.
const CustomTableBuilder = ({ document }) => {
  const [selectedFields, setSelectedFields] = useState([]);
  const [availableFields, setAvailableFields] = useState([]);
  const [customTableData, setCustomTableData] = useState([]); // State for the generated table

  // Effect to populate available fields when document data changes
  useEffect(() => {
    let fields = [];
    // Example: Extract fields from financial metrics (adjust based on actual structure)
    if (document?.financial_data?.metrics) {
      Object.entries(document.financial_data.metrics).forEach(([page, metrics]) => {
        Object.keys(metrics).forEach(metricKey => {
          fields.push(`Metric: ${metricKey} (Page ${Number(page) + 1})`);
        });
      });
    }
    // Example: Extract fields from table headers (adjust based on actual structure)
    if (document?.tables) {
       Object.entries(document.tables).forEach(([pageNum, pageTables]) => {
          if (Array.isArray(pageTables)) {
             pageTables.forEach((table, tableIndex) => {
                if (table.header && Array.isArray(table.header)) {
                   table.header.forEach(header => {
                      fields.push(`Table ${tableIndex + 1} (Page ${Number(pageNum) + 1}): ${header}`);
                   });
                }
             });
          }
       });
    }
    // Add more logic to extract fields from other parts of the document data
    setAvailableFields([...new Set(fields)]); // Remove duplicates
    setSelectedFields([]); // Reset selected fields when document changes
    setCustomTableData([]); // Reset table data
  }, [document]);

  const handleFieldChange = (event) => {
    const {
      target: { value },
    } = event;
    setSelectedFields(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value,
    );
  };

  const buildTable = () => {
    // Placeholder logic to build table data based on selected fields
    // This needs complex logic to map selected fields back to the actual data
    // in the document object and structure it into rows.
    console.log("Building table with fields:", selectedFields);
    const generatedData = selectedFields.map(field => ({
        field: field,
        value: `Value for ${field}` // Placeholder value
    }));
    setCustomTableData(generatedData);
  };

  return (
    <Paper elevation={1} sx={{ p: 3, mt: 3 }}> {/* Added margin top */}
      <Typography variant="h6" gutterBottom>Build Custom Table</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Select fields from the extracted data to create a custom table view.
      </Typography>

      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={8}>
          <FormControl fullWidth>
            <InputLabel id="custom-table-fields-label">Available Fields</InputLabel>
            <Select
              labelId="custom-table-fields-label"
              id="custom-table-fields-select"
              multiple
              value={selectedFields}
              onChange={handleFieldChange}
              label="Available Fields" // Connects to InputLabel
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {availableFields.length === 0 && <MenuItem disabled>No fields available</MenuItem>}
              {availableFields.map((field) => (
                <MenuItem key={field} value={field}>
                  {field}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <Button
            variant="contained"
            onClick={buildTable}
            disabled={selectedFields.length === 0}
            startIcon={<AddIcon />}
            fullWidth
          >
            Build Table
          </Button>
        </Grid>
      </Grid>

      {/* Display Custom Table */}
      {customTableData.length > 0 && (
        <Box mt={3}>
          <Typography variant="subtitle1" gutterBottom>Custom Table Result</Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Selected Field</TableCell>
                  <TableCell>Value (Placeholder)</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {customTableData.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.field}</TableCell>
                    <TableCell>{row.value}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
    </Paper>
  );
};

export default CustomTableBuilder;