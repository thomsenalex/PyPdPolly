# PyPdPolly
Convert pdf to mp3

The code utilizes slate to convert pdf to text and then AWS's Polly to synasize text to mp3. A s3 bucket is used to house the mp3 until downloaed. 

To utilize you will need an AWS account and there will be a small charge for Polly. If you're all set on AWS then simply run the dependencies and execute the code. See help for the command line arguements. Here is an example to get you started:

<code>python3 PyPdPolly.py -i example.pdf -o test.mp3 --title result --bucket alexrecordings2</code>

If the script fails there are some things to check:

1- Timeout of authentication because too many attempts have been made<br />
2- Ensure your S3 bucket is in the same location as your AWS default region
