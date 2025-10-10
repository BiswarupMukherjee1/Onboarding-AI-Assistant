"""
AWS Helper - Simplified AWS service interactions
"""

import boto3
from botocore.config import Config as BotoConfig
from config import config
import json
import time

class AWSHelper:
    """
    Unified helper for AWS service interactions
    """
    
    def __init__(self):
        self.boto_config = BotoConfig(
            region_name=config.REGION_NAME,
            connect_timeout=10,
            read_timeout=config.BEDROCK_TIMEOUT
        )
        
        # Initialize clients lazily
        self._bedrock_agent = None
        self._s3 = None
        self._dynamodb = None
        self._ses = None
        self._transcribe = None
        self._polly = None
    
    @property
    def bedrock_agent(self):
        """Get Bedrock Agent Runtime client"""
        if not self._bedrock_agent:
            self._bedrock_agent = boto3.client(
                'bedrock-agent-runtime',
                config=self.boto_config
            )
        return self._bedrock_agent
    
    @property
    def s3(self):
        """Get S3 client"""
        if not self._s3:
            self._s3 = boto3.client('s3', config=self.boto_config)
        return self._s3
    
    @property
    def dynamodb(self):
        """Get DynamoDB resource"""
        if not self._dynamodb:
            self._dynamodb = boto3.resource('dynamodb', config=self.boto_config)
        return self._dynamodb
    
    @property
    def ses(self):
        """Get SES client"""
        if not self._ses:
            self._ses = boto3.client('ses', config=self.boto_config)
        return self._ses
    
    @property
    def transcribe(self):
        """Get Transcribe client"""
        if not self._transcribe:
            self._transcribe = boto3.client('transcribe', config=self.boto_config)
        return self._transcribe
    
    @property
    def polly(self):
        """Get Polly client"""
        if not self._polly:
            self._polly = boto3.client('polly', config=self.boto_config)
        return self._polly
    
    def invoke_bedrock_agent(self, question, session_id, agent_id=None, agent_alias_id=None):
        """
        Invoke Bedrock agent with retry logic
        """
        agent_id = agent_id or config.AGENT_ID
        agent_alias_id = agent_alias_id or config.AGENT_ALIAS_ID
        
        for attempt in range(config.API_RETRY_COUNT):
            try:
                response = self.bedrock_agent.invoke_agent(
                    agentId=agent_id,
                    agentAliasId=agent_alias_id,
                    sessionId=session_id,
                    inputText=question
                )
                
                response_text = ""
                for event in response['completion']:
                    if 'chunk' in event:
                        response_text += event['chunk']['bytes'].decode('utf-8')
                
                return {
                    'success': True,
                    'response': response_text,
                    'session_id': session_id
                }
            
            except self.bedrock_agent.exceptions.InternalServerException:
                if attempt < config.API_RETRY_COUNT - 1:
                    time.sleep(config.API_RETRY_DELAY)
                else:
                    return {
                        'success': False,
                        'error': 'Service temporarily unavailable',
                        'response': 'Sorry, I am temporarily unavailable. Please try again.'
                    }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'response': f'Error: {str(e)}'
                }
    
    def upload_to_s3(self, file_path, s3_key, bucket=None):
        """
        Upload file to S3
        """
        bucket = bucket or config.S3_BUCKET
        
        try:
            self.s3.upload_file(file_path, bucket, s3_key)
            return {
                'success': True,
                'bucket': bucket,
                'key': s3_key,
                'url': f"s3://{bucket}/{s3_key}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_from_s3(self, s3_key, local_path, bucket=None):
        """
        Download file from S3
        """
        bucket = bucket or config.S3_BUCKET
        
        try:
            self.s3.download_file(bucket, s3_key, local_path)
            return {
                'success': True,
                'local_path': local_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_s3_objects(self, prefix='', bucket=None):
        """
        List objects in S3 bucket
        """
        bucket = bucket or config.S3_BUCKET
        
        try:
            response = self.s3.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            
            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
            
            return {
                'success': True,
                'objects': objects,
                'count': len(objects)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'objects': []
            }
    
    def save_to_dynamodb(self, table_name, item):
        """
        Save item to DynamoDB table
        """
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=item)
            return {
                'success': True,
                'table': table_name
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_from_dynamodb(self, table_name, key):
        """
        Get item from DynamoDB table
        """
        try:
            table = self.dynamodb.Table(table_name)
            response = table.get_item(Key=key)
            
            if 'Item' in response:
                return {
                    'success': True,
                    'item': response['Item']
                }
            else:
                return {
                    'success': False,
                    'error': 'Item not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_dynamodb(self, table_name, key_condition, expression_values):
        """
        Query DynamoDB table
        """
        try:
            table = self.dynamodb.Table(table_name)
            response = table.query(
                KeyConditionExpression=key_condition,
                ExpressionAttributeValues=expression_values
            )
            
            return {
                'success': True,
                'items': response.get('Items', []),
                'count': response.get('Count', 0)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'items': []
            }
    
    def send_email_ses(self, recipient, subject, html_body, sender=None):
        """
        Send email via SES
        """
        sender = sender or config.SES_SENDER_EMAIL
        
        try:
            response = self.ses.send_email(
                Source=sender,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            return {
                'success': True,
                'message_id': response['MessageId']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def transcribe_audio(self, audio_file_path, job_name=None):
        """
        Transcribe audio file using Amazon Transcribe
        """
        import uuid
        
        job_name = job_name or f"transcription_{uuid.uuid4()}"
        
        # Upload to S3 first
        s3_key = f"transcriptions/{job_name}.mp3"
        upload_result = self.upload_to_s3(audio_file_path, s3_key)
        
        if not upload_result['success']:
            return upload_result
        
        try:
            # Start transcription job
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': upload_result['url']},
                MediaFormat='mp3',
                LanguageCode='en-US'
            )
            
            # Wait for completion
            while True:
                status = self.transcribe.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                
                time.sleep(5)
            
            if job_status == 'COMPLETED':
                import requests
                transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                transcript_json = requests.get(transcript_url).json()
                transcript_text = transcript_json['results']['transcripts'][0]['transcript']
                
                return {
                    'success': True,
                    'transcript': transcript_text,
                    'job_name': job_name
                }
            else:
                return {
                    'success': False,
                    'error': 'Transcription failed'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def synthesize_speech(self, text, output_path, voice_id='Joanna'):
        """
        Synthesize speech using Amazon Polly
        """
        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id
            )
            
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            return {
                'success': True,
                'output_path': output_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def health_check(self):
        """
        Check health of AWS services
        """
        health = {
            's3': False,
            'dynamodb': False,
            'bedrock': False,
            'ses': False
        }
        
        # Check S3
        try:
            self.s3.list_buckets()
            health['s3'] = True
        except:
            pass
        
        # Check DynamoDB
        try:
            self.dynamodb.meta.client.list_tables()
            health['dynamodb'] = True
        except:
            pass
        
        # Check SES
        try:
            self.ses.get_send_quota()
            health['ses'] = True
        except:
            pass
        
        # Bedrock check (just verify client creation)
        try:
            _ = self.bedrock_agent
            health['bedrock'] = True
        except:
            pass
        
        return health

# Create singleton instance
aws_helper = AWSHelper()
