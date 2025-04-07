# Jamsters DS4300 Final Project
Run `streamlit run app.py` to access Streamlit app that allows file upload and shows final data. 

Adding files to the upload widget will load them to the S3 bucket specified in your .env file, which should be formatted as follows: 
```
AWS_ACCESS_KEY_ID='ABC123'
AWS_SECRET_ACCESS_KEY='ZYX987'
AWS_REGION='us-east-2'
S3_BUCKET_NAME='bucket-name'
```