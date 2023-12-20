import json
import boto3
import datetime

# Get the current timestamp
current_time = datetime.datetime.now()

# Format the timestamp as "ddmmyy"
timestamp = current_time.strftime("%d%m%y")

# Initialize AWS clients
s3_client = boto3.client('s3')
polly_client = boto3.client('polly')

def lambda_handler(event, context):
    # Define the source and destination S3 bucket and file names
    source_bucket = str(event["Records"][0]['s3']['bucket']['name']) #These are the details received from the S3 Event and we are gathering bucket name and File name of the same
    source_file_key = str(event["Records"][0]['s3']['object']['key'])
    destination_bucket = 'text2talk-target-audio-bucket' ## Update the target bucket name accordingly as per bucket name in your account
    destination_file_key = f"{timestamp}-audio.mp3"

    # Fetch the text content from the source S3 bucket
    try:
        response = s3_client.get_object(Bucket=source_bucket, Key=source_file_key)
        text = response['Body'].read().decode('utf-8')
    except Exception as e:
        print(str(e))
        return {
            'statusCode': 500,
            'body': f'Error fetching text from S3: {str(e)}'
        }

    # Use Amazon Polly to synthesize speech from the text
    try:
        response = polly_client.synthesize_speech(
            OutputFormat='mp3',
            Text=text,
            VoiceId='Salli'  # You can choose a different voice IDs too
        )
        audio_data = response['AudioStream'].read()
    except Exception as e:
        print(str(e))
        return {
            'statusCode': 500,
            'body': f'Error synthesizing speech with Polly: {str(e)}'
        }

    # Upload the MP3 audio to the destination S3 bucket
    try:
        s3_client.put_object(Bucket=destination_bucket, Key=destination_file_key, Body=audio_data)
    except Exception as e:
        print(str(e))
        return {
            'statusCode': 500,
            'body': f'Error uploading MP3 to S3: {str(e)}'
        }
    print("success")    

    return {
        'statusCode': 200,
        'body': f'Successfully converted and saved text to MP3: s3://{destination_bucket}/{destination_file_key}'
    }