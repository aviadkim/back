import os
import boto3
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

def test_aws_textract_connection():
    """
    בדיקת חיבור ל-AWS Textract
    """
    # קריאת מפתחות AWS מקובץ .env
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-1')
    
    if not aws_access_key or not aws_secret_key:
        print("חסרים מפתחות AWS ב-.env")
        print("יש להוסיף AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ו-AWS_REGION (אופציונלי)")
        return False
    
    try:
        # יצירת קליינט טקסטרקט
        textract = boto3.client(
            'textract',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # יצירת תמונת טקסט פשוטה לבדיקה
        text_image = create_test_image("בדיקת OCR בענן עובדת!")
        
        # המרת התמונה ל-bytes
        img_byte_arr = io.BytesIO()
        text_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # שליחה ל-Textract
        response = textract.detect_document_text(
            Document={'Bytes': img_byte_arr}
        )
        
        # בדיקת התוצאה
        extracted_text = ""
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                extracted_text += item['Text'] + "\n"
        
        print("תוצאת ה-OCR:")
        print(extracted_text)
        
        if "בדיקת OCR" in extracted_text:
            print("בדיקת החיבור ל-AWS Textract עברה בהצלחה!")
            return True
        else:
            print("ה-OCR הצליח אך הטקסט לא זוהה כראוי")
            return False
        
    except Exception as e:
        print(f"שגיאה בחיבור ל-AWS Textract: {e}")
        return False

def create_test_image(text):
    """
    יצירת תמונת טקסט פשוטה לבדיקת OCR
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # יצירת תמונה לבנה
        image = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(image)
        
        # הוספת טקסט
        try:
            font = ImageFont.truetype('arial.ttf', size=24)
        except IOError:
            font = ImageFont.load_default()
        
        draw.text((20, 40), text, fill='black', font=font)
        
        return image
        
    except Exception as e:
        print(f"שגיאה ביצירת תמונת טקסט: {e}")
        # יצירת תמונה פשוטה יותר במקרה של שגיאה
        return Image.new('RGB', (400, 100), color='white')

if __name__ == "__main__":
    print("בודק חיבור ל-AWS Textract...")
    test_aws_textract_connection()