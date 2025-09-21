# Onboarding-AI-Assistant

## Bedrock | AI AGENT | Knowledge Base
An AI-powered onboarding assistant built to boost new hire productivity, minimize manual support workload, and deliver instant, conversational assistance through voice and text using Generative AI. Also this solution assess the employee readiness for project deployment.

## ⚙️ Key Components:

1. Conversational Interface: For voice/text-based interaction
2. Document Insights Engine: Extracts knowledge from KT docs, PDFs, reports
3. FAQ & Troubleshooting Module: Handles repetitive queries and pipeline errors
4. Personalized Assistant Logic: Adapts to user role, team, and tech stack
5. Analytics Dashboard: Tracks usage, gaps, and improvement areas

## AWS Services Utilized:

1. Amazon Bedrock Agent: Model access for LLM-driven responses

2. Amazon S3: Stores documentation, reports, and FAQs

3. Amazon Sage Maker ai : For code development and Testing

4. Amazon EC2 : For deploying streamlit application

5. Amazon Polly: Converts text responses to natural-sounding speech

6. Amazon Transcribe: Transcribes user voice input to text


## Setup

This Application will run in Amazon sage maker AI and Amazon EC2 as well
1. Configure your AWS credentials:
- > o Make sure you have AWS credentials configured with permissions to access Amazon Bedrock
- > o You can configure credentials using AWS CLI: aws configure
2. Update the files with Agent Id and Agent Alias id.
3. Running the Voice Agent
4. Run streamlit app using streamlit run voiceagent.py
5. This will automatically call chatagent as well
6. Open your browser and navigate to Local URL 
7. You can either speak or chat it will provide options to choose

