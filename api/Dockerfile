# משתמש בתמונת בסיס של Python
FROM python:3.9-slim

# הגדרת משתני סביבה
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# התקנת חבילות נדרשות
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-heb \
    poppler-utils \
    libpoppler-dev \
    libpoppler-cpp-dev \
    pkg-config \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    wget \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# יצירת תיקיית העבודה ומעבר אליה
WORKDIR /app

# העתקת קובץ הדרישות והתקנת הספריות הנדרשות
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# הוספת תלויות נוספות שדרושות לקוד המשופר
RUN pip install --no-cache-dir \
    timm \
    tabulate \
    matplotlib \
    easyocr \
    huggingface-hub \
    fastapi \
    uvicorn \
    python-multipart

# העתקת שאר הקבצים לתיקיית העבודה
COPY ../scripts /app/scripts
COPY ../models /app/models
COPY . /app/api

# חשיפת פורט 8000 עבור ה-API
EXPOSE 8000

# הרצת שרת ה-API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 