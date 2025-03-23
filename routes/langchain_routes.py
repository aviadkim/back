from flask import Blueprint, request, jsonify
import os
import json
import logging
from dotenv import load_dotenv
import openai

# טעינת משתני סביבה
load_dotenv()

# הגדרת מפתח ה-API של OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# יצירת Mistral או Claude API key
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')

langchain_bp = Blueprint('langchain', __name__)
logger = logging.getLogger(__name__)

@langchain_bp.route('/chat/message', methods=['POST'])
def process_chat_message():
    """עיבוד הודעת צ'אט עם מודל שפה לניתוח מסמכים פיננסיים."""
    try:
        data = request.form
        message = data.get('message', '')
        context = data.get('context', '{}')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
            
        # המרת הקונטקסט ל-JSON
        try:
            context_data = json.loads(context)
        except json.JSONDecodeError:
            context_data = {}
            
        # הכנת הקונטקסט עבור המודל שפה
        system_message = """
        אתה עוזר דיגיטלי מומחה לניתוח מסמכים פיננסיים. תפקידך לענות על שאלות ולנתח מידע מתוך מסמכים פיננסיים.
        כשאתה מתבקש לנתח מידע, השתמש במידע הקיים בקונטקסט.
        במידה ומבקשים ממך מידע שאינו בקונטקסט, ציין זאת בבירור.
        כשמדובר בטבלאות, נסה לארגן את המידע באופן מובנה.
        """
        
        # בחירת המודל המתאים
        if MISTRAL_API_KEY:
            response = process_with_mistral(message, context_data, system_message)
        elif CLAUDE_API_KEY:
            response = process_with_anthropic(message, context_data, system_message)
        elif openai.api_key:
            response = process_with_openai(message, context_data, system_message)
        else:
            return jsonify({'error': 'No API key configured for language models'}), 500
            
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_with_mistral(message, context, system_message):
    """עיבוד הודעת צ'אט באמצעות Mistral API."""
    import requests
    
    api_url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    
    # בניית ההודעות
    messages = [
        {"role": "system", "content": system_message}
    ]
    
    # הוספת הקונטקסט אם יש נתונים
    document_id = context.get('documentId')
    document_data = context.get('documentData')
    
    if document_data:
        context_text = f"מידע על המסמך:\n\n"
        
        if isinstance(document_data, dict):
            # הוספת מידע על המסמך
            if 'filename' in document_data:
                context_text += f"שם קובץ: {document_data.get('filename')}\n"
            if 'total_pages' in document_data:
                context_text += f"סה\"כ עמודים: {document_data.get('total_pages')}\n"
                
            # הוספת טקסט מהמסמך
            if 'pages' in document_data:
                for page_num, page_data in document_data.get('pages', {}).items():
                    if 'text' in page_data:
                        context_text += f"\nטקסט מעמוד {page_num}:\n{page_data.get('text')[:1000]}...\n"
                        
                    # הוספת מידע על טבלאות
                    if 'tables' in page_data and page_data['tables']:
                        context_text += f"\nנמצאו {len(page_data['tables'])} טבלאות בעמוד {page_num}.\n"
        
        messages.append({"role": "user", "content": context_text})
        messages.append({"role": "assistant", "content": "תודה על המידע. אני מוכן לענות על שאלות לגבי המסמך."})
    
    # הוספת הודעת המשתמש
    messages.append({"role": "user", "content": message})
    
    # שליחת הבקשה ל-API
    data = {
        "model": "mistral-large-latest",
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(api_url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        assistant_message = response_data['choices'][0]['message']['content']
        
        # בדיקה אם יש נתונים מובנים שניתן להציג בטבלה
        table_data = extract_table_data(assistant_message)
        
        return {
            'message': assistant_message,
            'data': {
                'tableData': table_data if table_data else None
            }
        }
    else:
        logger.error(f"Mistral API Error: {response.text}")
        return {'message': 'אירעה שגיאה בעיבוד הבקשה.'}

def process_with_anthropic(message, context, system_message):
    """עיבוד הודעת צ'אט באמצעות Anthropic Claude API."""
    from anthropic import Anthropic
    
    client = Anthropic(api_key=CLAUDE_API_KEY)
    
    # בניית הפרומפט
    prompt = f"{system_message}\n\n"
    
    # הוספת הקונטקסט אם יש נתונים
    document_id = context.get('documentId')
    document_data = context.get('documentData')
    
    if document_data:
        prompt += f"מידע על המסמך:\n\n"
        
        if isinstance(document_data, dict):
            # הוספת מידע על המסמך
            if 'filename' in document_data:
                prompt += f"שם קובץ: {document_data.get('filename')}\n"
            if 'total_pages' in document_data:
                prompt += f"סה\"כ עמודים: {document_data.get('total_pages')}\n"
                
            # הוספת טקסט מהמסמך
            if 'pages' in document_data:
                for page_num, page_data in document_data.get('pages', {}).items():
                    if 'text' in page_data:
                        prompt += f"\nטקסט מעמוד {page_num}:\n{page_data.get('text')[:1000]}...\n"
                        
                    # הוספת מידע על טבלאות
                    if 'tables' in page_data and page_data['tables']:
                        prompt += f"\nנמצאו {len(page_data['tables'])} טבלאות בעמוד {page_num}.\n"
    
    # הוספת הודעת המשתמש
    prompt += f"\nשאלת המשתמש: {message}\n"
    
    # שליחת הבקשה ל-API
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.7,
        system=system_message,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    assistant_message = response.content[0].text
    
    # בדיקה אם יש נתונים מובנים שניתן להציג בטבלה
    table_data = extract_table_data(assistant_message)
    
    return {
        'message': assistant_message,
        'data': {
            'tableData': table_data if table_data else None
        }
    }

def process_with_openai(message, context, system_message):
    """עיבוד הודעת צ'אט באמצעות OpenAI API."""
    # בניית ההודעות
    messages = [
        {"role": "system", "content": system_message}
    ]
    
    # הוספת הקונטקסט אם יש נתונים
    document_id = context.get('documentId')
    document_data = context.get('documentData')
    
    if document_data:
        context_text = f"מידע על המסמך:\n\n"
        
        if isinstance(document_data, dict):
            # הוספת מידע על המסמך
            if 'filename' in document_data:
                context_text += f"שם קובץ: {document_data.get('filename')}\n"
            if 'total_pages' in document_data:
                context_text += f"סה\"כ עמודים: {document_data.get('total_pages')}\n"
                
            # הוספת טקסט מהמסמך
            if 'pages' in document_data:
                for page_num, page_data in document_data.get('pages', {}).items():
                    if 'text' in page_data:
                        context_text += f"\nטקסט מעמוד {page_num}:\n{page_data.get('text')[:1000]}...\n"
                        
                    # הוספת מידע על טבלאות
                    if 'tables' in page_data and page_data['tables']:
                        context_text += f"\nנמצאו {len(page_data['tables'])} טבלאות בעמוד {page_num}.\n"
        
        messages.append({"role": "user", "content": context_text})
        messages.append({"role": "assistant", "content": "תודה על המידע. אני מוכן לענות על שאלות לגבי המסמך."})
    
    # הוספת הודעת המשתמש
    messages.append({"role": "user", "content": message})
    
    # שליחת הבקשה ל-API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )
    
    assistant_message = response.choices[0].message.content
    
    # בדיקה אם יש נתונים מובנים שניתן להציג בטבלה
    table_data = extract_table_data(assistant_message)
    
    return {
        'message': assistant_message,
        'data': {
            'tableData': table_data if table_data else None
        }
    }

def extract_table_data(text):
    """חילוץ נתוני טבלה מטקסט."""
    import re
    
    # חיפוש טבלאות בפורמט markdown
    table_pattern = r'(\|.*\|\n\|[-:| ]+\|\n(?:\|.*\|\n)+)'
    tables = re.findall(table_pattern, text)
    
    if not tables:
        return None
        
    # נבחר את הטבלה הראשונה
    table_text = tables[0]
    
    # פירוק הטבלה לשורות
    rows = [row.strip() for row in table_text.split('\n') if row.strip()]
    
    # דילוג על שורת המפריד (---|---|---)
    header_row = rows[0]
    data_rows = rows[2:]
    
    # חילוץ הכותרות
    headers = [cell.strip() for cell in header_row.split('|')[1:-1]]
    
    # חילוץ הנתונים
    data = []
    for row in data_rows:
        cells = [cell.strip() for cell in row.split('|')[1:-1]]
        data.append(cells)
    
    return {
        'headers': headers,
        'data': data
    }

@langchain_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    """קבלת היסטוריית צ'אט."""
    # במערכת אמיתית, היסטוריית השיחה תישמר בבסיס נתונים
    # כרגע מחזירים רשימה ריקה
    return jsonify([]), 200

@langchain_bp.route('/chat/history', methods=['DELETE'])
def clear_chat_history():
    """ניקוי היסטוריית צ'אט."""
    # במערכת אמיתית, נמחק את היסטוריית השיחה מבסיס הנתונים
    return jsonify({'status': 'success', 'message': 'Chat history cleared'}), 200

@langchain_bp.route('/templates', methods=['POST'])
def save_template():
    """שמירת תבנית טבלה."""
    try:
        template_data = request.json
        
        if not template_data or 'name' not in template_data or 'headers' not in template_data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # במערכת אמיתית, התבנית תישמר בבסיס נתונים
        # כרגע מדמה הצלחה
        
        return jsonify({
            'status': 'success',
            'message': 'Template saved successfully',
            'template_id': f"template_{hash(template_data['name'])}"
        }), 201
        
    except Exception as e:
        logger.error(f"Error saving template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/templates', methods=['GET'])
def get_templates():
    """קבלת רשימת תבניות שמורות."""
    # במערכת אמיתית, התבניות יישלפו מבסיס נתונים
    # כרגע מחזירים רשימה לדוגמה
    
    sample_templates = [
        {
            'id': 'template_1',
            'name': 'תבנית אגרות חוב',
            'headers': ['שם נייר', 'מח"מ', 'תשואה', 'ערך נקוב', 'שווי'],
            'originalHeaders': ['Bond Name', 'Duration', 'Yield', 'Par Value', 'Value'],
            'created_at': '2025-03-20T10:30:00Z'
        },
        {
            'id': 'template_2',
            'name': 'תבנית מניות',
            'headers': ['שם חברה', 'סימול', 'ענף', 'מחיר', 'שינוי יומי', 'כמות'],
            'originalHeaders': ['Company', 'Symbol', 'Sector', 'Price', 'Daily Change', 'Quantity'],
            'created_at': '2025-03-21T14:15:00Z'
        }
    ]
    
    return jsonify(sample_templates), 200

@langchain_bp.route('/templates/<template_id>/apply', methods=['POST'])
def apply_template(template_id):
    """החלת תבנית על טבלה."""
    try:
        data = request.json
        document_id = data.get('document_id')
        
        if not document_id:
            return jsonify({'error': 'Missing document_id'}), 400
            
        # במערכת אמיתית, התבנית והנתונים יישלפו מבסיס נתונים
        # ותבוצע התאמה אוטומטית של הנתונים לכותרות התבנית
        
        # לדוגמה, נחזיר נתונים מדומים
        
        # חיפוש תבנית לפי מזהה
        sample_templates = [
            {
                'id': 'template_1',
                'name': 'תבנית אגרות חוב',
                'headers': ['שם נייר', 'מח"מ', 'תשואה', 'ערך נקוב', 'שווי'],
                'originalHeaders': ['Bond Name', 'Duration', 'Yield', 'Par Value', 'Value']
            },
            {
                'id': 'template_2',
                'name': 'תבנית מניות',
                'headers': ['שם חברה', 'סימול', 'ענף', 'מחיר', 'שינוי יומי', 'כמות'],
                'originalHeaders': ['Company', 'Symbol', 'Sector', 'Price', 'Daily Change', 'Quantity']
            }
        ]
        
        template = next((t for t in sample_templates if t['id'] == template_id), None)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
            
        # דוגמה לנתונים ממופים לפי התבנית
        if template_id == 'template_1':
            # נתוני אגרות חוב לדוגמה
            mapped_data = [
                ['אג"ח ממשלתי 0326', '2.5', '3.2%', '10,000', '9,800'],
                ['אג"ח חברה א', '3.7', '4.5%', '5,000', '5,100'],
                ['אג"ח דולרי', '5.2', '2.8%', '20,000', '19,500']
            ]
        else:
            # נתוני מניות לדוגמה
            mapped_data = [
                ['חברה א', 'AAA', 'טכנולוגיה', '120.5', '+2.3%', '1,000'],
                ['חברה ב', 'BBB', 'אנרגיה', '85.2', '-1.1%', '2,500'],
                ['חברה ג', 'CCC', 'פיננסים', '210.7', '+0.5%', '500']
            ]
            
        return jsonify({
            'status': 'success',
            'template': template,
            'mappedData': mapped_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error applying template: {str(e)}")
        return jsonify({'error': str(e)}), 500