# importing required modules 
from concurrent.futures import thread
import slate3k as slate
import time
import sys, getopt, os
import boto3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import threading
from tempfile import gettempdir


# Create a client using the credentials and region defined in the aws profile
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="default")
polly = session.client("polly")


#main logic
def main(argv):
    inputfile = ''
    outputfile = ''
    large = ""
    s3 = ""
    title = ""
    try:
        opts, args = getopt.getopt(argv,"hi:o:b:t:l",["help","ifile=","ofile=","bucket=","title=","large"])
    except getopt.GetoptError as e:
        print('test.py -i <inputfile> -o <outputfile>')
        print(e)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-l", "--large"):
            large = "true"
        elif opt in ("--bucket"):
            s3 = arg
        elif opt in ("-t", "--title"):
            title = arg

    if(large=="true"):
        if(s3 == ""):
            s3 = input("Enter the s3 bucket name: ")
        if(title == ""):
            title = input("Enter the file name: ")

    with open(inputfile, 'rb') as f:
        extracted_text = slate.PDF(f)
   
    culminatedText = ""

    for page in extracted_text:
        culminatedText = culminatedText + page

    charLength = 30000
    split_strings = [culminatedText[index : index + charLength] for index in range(0, len(culminatedText), charLength)]
    
    #pollyize each chapter
    numChapters = len(split_strings)
    print("Synthing "+str(numChapters)+" chapters")
    threads = []
    for indx, chapter in enumerate(split_strings) :
        threads.append(threading.Thread(target=pollyizeLarge, args=(chapter,s3,title,(indx+1))))

    for indvThread in threads:
        indvThread.start()

    for joinIndvThread in threads:
        joinIndvThread.join()

    print("Finished")

        

def pollyizeLarge(input,s3Name,title,chapterNum):

    s3_client = boto3.client('s3', region_name="us-east-1")
    location = {'LocationConstraint': "us-east-1"}
    try:
        s3_client.create_bucket(Bucket=s3Name)
    except:
        print("Confirmed bucket exists")
    title= title+"-ch"+str(chapterNum)+"_"
    input = input
    response = polly.start_speech_synthesis_task(VoiceId='Joanna',
                OutputS3BucketName=s3Name,
                OutputS3KeyPrefix=title,
                OutputFormat='mp3', 
                Text=input,
                Engine='neural')

    taskId = response['SynthesisTask']['TaskId']

    print( "Task id is {} ".format(taskId))

    
    print("Pushing chapter "+str(chapterNum)+"\n")  
    isComplete="false"
    while(isComplete=="false"):
        task_status = polly.get_speech_synthesis_task(TaskId = taskId)
        status = task_status['SynthesisTask']['TaskStatus']

        if(status=='completed'):
            print("Finished, see S3 bucket for file.")
            isComplete="true" 

        elif(status=='failed'):
            print("Failed synthasizing see AWS account for more details")
            print(task_status)
            return()
        else:
            time.sleep(5)
            print("Chapter "+str(chapterNum)+','+status)

    #download created file
    s3FileName = title+"."+taskId+'.mp3'
    s3_client.download_file(s3Name,s3FileName,(title+".mp3"))
    print(s3FileName+" downloaded.")

if __name__ == "__main__":
   main(sys.argv[1:])