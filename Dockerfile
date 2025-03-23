FROM python:3.9-slim

WORKDIR /app

# התקנת תלויות OS
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    tesseract-ocr-eng \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# העתקת קבצי הפרויקט
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# יצירת תיקיות נדרשות
RUN mkdir -p uploads data data/embeddings data/templates logs

# הגדרת משתני סביבה
ENV FLASK_ENV=production
ENV PORT=5000

# הגדרת פקודת הרצה
CMD gunicorn --bind 0.0.0.0:$PORT app:app