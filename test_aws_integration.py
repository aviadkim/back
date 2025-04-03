#!/usr/bin/env python3
import os
import requests
import json
import sys
import time
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# כתובת השרת
SERVER_URL = 'http://localhost:5000'

def test_aws_health():
    """בדיקת תקינות שירותי AWS"""
    try:
        logger.info("Testing AWS health...")
        response = requests.get(f"{SERVER_URL}/api/aws/health")
        if response.status_code == 200:
            logger.info(f"AWS health check successful: {response.json()}")
            return True
        else:
            logger.error(f"AWS health check failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing AWS health: {str(e)}")
        return False

def test_upload_document(file_path):
    """בדיקת העלאת מסמך"""
    try:
        logger.info(f"Uploading document: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        files = {'file': open(file_path, 'rb')}
        data = {'language': 'auto'}

        response = requests.post(f"{SERVER_URL}/api/aws/upload", files=files, data=data)

        if response.status_code == 202:
            result = response.json()
            document_id = result['document_id']
            logger.info(f"Upload successful: {document_id}")
            return document_id
        else:
            logger.error(f"Upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return False

def test_get_document_data(document_id):
    """בדיקת קבלת נתוני מסמך"""
    try:
        logger.info(f"Getting document data: {document_id}")

        # המתנה לעיבוד
        for _ in range(10):  # ניסיון 10 פעמים
            response = requests.get(f"{SERVER_URL}/api/aws/documents/{document_id}")

            if response.status_code == 200:
                data = response.json()
                status = data.get('metadata', {}).get('status')

                if status == 'completed':
                    logger.info("Document processing completed")
                    return data
                elif status == 'error':
                    logger.error(f"Document processing failed: {data}")
                    return False
                else:
                    logger.info(f"Document still processing, status: {status}")
                    time.sleep(5)  # המתנה 5 שניות
            else:
                logger.error(f"Error getting document: {response.status_code} - {response.text}")
                time.sleep(5)

        logger.error("Timeout waiting for document processing")
        return False
    except Exception as e:
        logger.error(f"Error getting document data: {str(e)}")
        return False

def test_ask_question(document_id, question):
    """בדיקת שאילת שאלה"""
    try:
        logger.info(f"Asking question about document {document_id}: {question}")

        data = {'question': question}
        headers = {'Content-Type': 'application/json'}

        response = requests.post(
            f"{SERVER_URL}/api/aws/documents/{document_id}/ask",
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"Question answered: {result['answer'][:100]}...")
            return result
        else:
            logger.error(f"Question failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error asking question: {str(e)}")
        return False

def test_get_tables(document_id):
    """בדיקת קבלת טבלאות"""
    try:
        logger.info(f"Getting tables for document {document_id}")

        response = requests.get(f"{SERVER_URL}/api/aws/documents/{document_id}/tables")

        if response.status_code == 200:
            tables = response.json()
            logger.info(f"Retrieved {len(tables)} tables")
            return tables
        else:
            logger.error(f"Error getting tables: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error getting tables: {str(e)}")
        return False

def main():
    """פונקציה ראשית"""

    # בדיקת תקינות
    if not test_aws_health():
        logger.error("AWS health check failed, exiting")
        return False

    # בדיקת נתיב הקובץ
    if len(sys.argv) < 2:
        logger.error("Please provide a PDF file path as argument")
        return False

    file_path = sys.argv[1]

    # העלאת מסמך
    document_id = test_upload_document(file_path)
    if not document_id:
        logger.error("Document upload failed, exiting")
        return False

    # קבלת נתוני מסמך
    document_data = test_get_document_data(document_id)
    if not document_data:
        logger.error("Getting document data failed, exiting")
        return False

    # שאילת שאלה
    question = "מה סוג המסמך ומה המידע העיקרי שהוא מכיל?"
    answer = test_ask_question(document_id, question)
    if not answer:
        logger.warning("Question answering failed")

    # קבלת טבלאות
    tables = test_get_tables(document_id)
    if not tables:
        logger.warning("Getting tables failed")

    logger.info("Test completed successfully!")
    return True

if __name__ == "__main__":
    main()