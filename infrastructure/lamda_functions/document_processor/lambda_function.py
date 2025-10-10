"""
Document Processor Lambda Function
Processes uploaded documents and extracts content for knowledge base
"""

import json
import boto3
import logging
from datetime import datetime
import uuid

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
textract = boto3.client('textract')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS SETUP updation
DYNAMODB_TABLE = 'onboarding-documents'  # Change to table name
S3_BUCKET = 'storevoice'  # Change to bucket name

def lambda_handler(event, context):
    """
    Lambda handler triggered by S3 upload events
    """
    try:
        logger.info(f"Processing event: {json.dumps(event)}")
        
        # Get S3 event details
        for record in event.get('Records', []):
            if record.get('eventName', '').startswith('ObjectCreated'):
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                
                logger.info(f"Processing document: s3://{bucket}/{key}")
                
                # Process the document
                result = process_document(bucket, key)
                
                if result['success']:
                    logger.info(f"Successfully processed {key}")
                else:
                    logger.error(f"Failed to process {key}: {result.get('error')}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Documents processed successfully'
            })
        }
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def process_document(bucket, key):
    """
    Process a single document using Amazon Textract
    """
    try:
        # Extract text from document
        if key.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(bucket, key)
        elif key.lower().endswith(('.doc', '.docx')):
            extracted_text = extract_text_from_doc(bucket, key)
        elif key.lower().endswith('.txt'):
            extracted_text = extract_text_from_txt(bucket, key)
        else:
            return {
                'success': False,
                'error': f'Unsupported file type: {key}'
            }
        
        # Store in DynamoDB
        store_document_metadata(key, extracted_text)
        
        return {
            'success': True,
            'text_length': len(extracted_text)
        }
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def extract_text_from_pdf(bucket, key):
    """
    Extract text from PDF using Amazon Textract
    """
    try:
        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )
        
        text = ""
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text += block['Text'] + "\n"
        
        return text
    
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        return ""

def extract_text_from_doc(bucket, key):
    """
    Extract text from Word document
    """
    try:
        # Download file from S3
        local_path = f"/tmp/{key.split('/')[-1]}"
        s3.download_file(bucket, key, local_path)
        
        # Extract text using python-docx
        import docx
        doc = docx.Document(local_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        
        return text
    
    except Exception as e:
        logger.error(f"Error extracting DOC text: {str(e)}")
        return ""

def extract_text_from_txt(bucket, key):
    """
    Extract text from TXT file
    """
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        text = obj['Body'].read().decode('utf-8')
        return text
    
    except Exception as e:
        logger.error(f"Error extracting TXT: {str(e)}")
        return ""

def store_document_metadata(key, extracted_text):
    """
    Store document metadata in DynamoDB
    """
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        document_id = str(uuid.uuid4())
        
        item = {
            'document_id': document_id,
            'file_name': key,
            'extracted_text': extracted_text[:5000],  # Store first 5000 chars
            'text_length': len(extracted_text),
            'processed_at': datetime.now().isoformat(),
            'status': 'processed'
        }
        
        table.put_item(Item=item)
        logger.info(f"Stored metadata for document {document_id}")
        
    except Exception as e:
        logger.error(f"Error storing metadata: {str(e)}")
        raise
