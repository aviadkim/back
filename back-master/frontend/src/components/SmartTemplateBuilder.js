import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Grid,
  Card,
  CardContent,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Check as CheckIcon,
  ContentCopy as ContentCopyIcon,
  TableChart as TableChartIcon
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import api from '../services/api';

const SmartTemplateBuilder = ({ pdfFile, onTemplateCreate }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [headers, setHeaders] = useState([]);
  const [selectedHeaders, setSelectedHeaders] = useState([]);
  const [templateName, setTemplateName] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [currentTemplate, setCurrentTemplate] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [error, setError] = useState(null);

  // שלבי הסטפר
  const steps = [
    'סריקת כותרות',
    'בחירת שדות',
    'הגדרת תבנית',
    'תצוגה מקדימה'
  ];

  // טעינת תבניות שמורות
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await api.templates.getTemplates();
        setTemplates(response.data);
      } catch (error) {
        console.error('שגיאה בטעינת תבניות:', error);
        setError('שגיאה בטעינת תבניות');
      }
    };
    loadTemplates();
  }, []);

  // סריקת כותרות מהמסמך
  const scanHeaders = async () => {
    setIsScanning(true);
    setError(null);
    try {
      const response = await api.templates.scanHeaders(pdfFile);
      setHeaders(response.headers.map((header, index) => ({
        id: index + 1,
        text: header,
        type: detectHeaderType(header)
      })));
    } catch (error) {
      console.error('שגיאה בסריקת כותרות:', error);
      setError('שגיאה בסריקת כותרות מהמסמך');
    } finally {
      setIsScanning(false);
    }
  };

  // זיהוי סוג הכותרת
  const detectHeaderType = (header) => {
    const headerLower = header.toLowerCase();
    if (headerLower.includes('date') || headerLower.includes('תאריך')) return 'date';
    if (headerLower.includes('amount') || headerLower.includes('סכום') || headerLower.includes('usd')) return 'currency';
    if (headerLower.includes('isin')) return 'code';
    if (headerLower.includes('number') || headerLower.includes('מספר')) return 'number';
    return 'text';
  };

  // הוספת כותרת לתבנית
  const handleHeaderSelect = (header) => {
    if (!selectedHeaders.some(h => h.id === header.id)) {
      setSelectedHeaders(prev => [...prev, { ...header, rules: [] }]);
    }
  };

  // שמירת תבנית
  const saveTemplate = async () => {
    try {
      const newTemplate = {
        name: templateName,
        headers: selectedHeaders,
        created: new Date().toISOString()
      };
      
      const response = await api.templates.saveTemplate(newTemplate);
      setTemplates(prev => [...prev, response.data]);
      setShowTemplateDialog(false);
      onTemplateCreate?.(response.data);
    } catch (error) {
      console.error('שגיאה בשמירת התבנית:', error);
      setError('שגיאה בשמירת התבנית');
    }
  };

  // תצוגה מקדימה של התבנית
  const previewTemplate = async () => {
    try {
      const response = await api.templates.applyTemplate(pdfFile, {
        headers: selectedHeaders.map(h => h.text)
      });
      setPreviewData(response);
    } catch (error) {
      console.error('שגיאה בתצוגה מקדימה:', error);
      setError('שגיאה בהפעלת התבנית על המסמך');
    }
  };

  // רינדור שלב סריקת הכותרות
  const renderScanStep = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        סריקת כותרות מהמסמך
      </Typography>
      {error && (
        <Typography color="error" gutterBottom>
          {error}
        </Typography>
      )}
      <Button
        variant="contained"
        color="primary"
        onClick={scanHeaders}
        disabled={isScanning}
        startIcon={isScanning ? <CircularProgress size={20} /> : <TableChartIcon />}
      >
        {isScanning ? 'סורק...' : 'התחל סריקה'}
      </Button>
      
      <Box sx={{ mt: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {headers.map((header) => (
          <Chip
            key={header.id}
            label={header.text}
            onClick={() => handleHeaderSelect(header)}
            color={selectedHeaders.some(h => h.id === header.id) ? 'primary' : 'default'}
            variant={selectedHeaders.some(h => h.id === header.id) ? 'filled' : 'outlined'}
          />
        ))}
      </Box>
    </Box>
  );

  // רינדור שלב בחירת השדות
  const renderSelectStep = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        ארגון שדות נבחרים
      </Typography>
      <DragDropContext onDragEnd={(result) => {
        if (!result.destination) return;
        const items = Array.from(selectedHeaders);
        const [reorderedItem] = items.splice(result.source.index, 1);
        items.splice(result.destination.index, 0, reorderedItem);
        setSelectedHeaders(items);
      }}>
        <Droppable droppableId="headers">
          {(provided) => (
            <Box {...provided.droppableProps} ref={provided.innerRef}>
              {selectedHeaders.map((header, index) => (
                <Draggable key={header.id} draggableId={String(header.id)} index={index}>
                  {(provided) => (
                    <Paper
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      sx={{ p: 2, mb: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                    >
                      <Typography>{header.text}</Typography>
                      <IconButton onClick={() => {
                        setSelectedHeaders(prev => prev.filter(h => h.id !== header.id));
                      }}>
                        <DeleteIcon />
                      </IconButton>
                    </Paper>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Box>
          )}
        </Droppable>
      </DragDropContext>
    </Box>
  );

  // רינדור שלב הגדרת התבנית
  const renderTemplateStep = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        הגדרת תבנית
      </Typography>
      <TextField
        fullWidth
        label="שם התבנית"
        value={templateName}
        onChange={(e) => setTemplateName(e.target.value)}
        sx={{ mb: 3 }}
      />
      <Button
        variant="contained"
        color="primary"
        onClick={saveTemplate}
        disabled={!templateName}
        startIcon={<SaveIcon />}
      >
        שמור תבנית
      </Button>
    </Box>
  );

  // רינדור שלב התצוגה המקדימה
  const renderPreviewStep = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        תצוגה מקדימה
      </Typography>
      {previewData ? (
        <Paper sx={{ overflow: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {previewData.headers.map((header, i) => (
                  <th key={i} style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5' }}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewData.rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex} style={{ border: '1px solid #ddd', padding: '8px' }}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Paper>
      ) : (
        <Button
          variant="contained"
          color="primary"
          onClick={previewTemplate}
          startIcon={<VisibilityIcon />}
        >
          צפה בתוצאות
        </Button>
      )}
    </Box>
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ mt: 2 }}>
        {activeStep === 0 && renderScanStep()}
        {activeStep === 1 && renderSelectStep()}
        {activeStep === 2 && renderTemplateStep()}
        {activeStep === 3 && renderPreviewStep()}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button
          onClick={() => setActiveStep((prev) => prev - 1)}
          disabled={activeStep === 0}
        >
          חזור
        </Button>
        <Button
          variant="contained"
          onClick={() => {
            if (activeStep === steps.length - 1) {
              onTemplateCreate?.(currentTemplate);
            } else {
              setActiveStep((prev) => prev + 1);
            }
          }}
          disabled={
            (activeStep === 0 && headers.length === 0) ||
            (activeStep === 1 && selectedHeaders.length === 0) ||
            (activeStep === 2 && !templateName)
          }
        >
          {activeStep === steps.length - 1 ? 'סיים' : 'הבא'}
        </Button>
      </Box>
    </Box>
  );
};

export default SmartTemplateBuilder; 