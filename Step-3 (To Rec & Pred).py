from tkinter import Y
import sounddevice as sd
from scipy.io.wavfile import write 

from random import sample
import librosa
import librosa.display

import tensorflow as tf
import tensorflow.keras as keras
import numpy as np

import keyboard
import time
import os

import soundfile as sf
from twilio.rest import Client

model=tf.keras.models.load_model('Dataset path')
    
def record():
    fs = 44100  # Sample rate
    seconds = 10  # Duration of recording

    print("Recording......")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    # Wait until recording is finished
    sd.wait()  

    print("Saving.....")
    # Saving file as Noisy_output.wav
    write('Noisy_output.wav', fs, myrecording) 
    
    print("Removing Noise.....")
    #load sample audio
    filename ='Noisy_output.wav'
    audio, sr = librosa.load(path=filename)

    #get intervals which are non-silent
    inter_10 = librosa.effects.split(y=audio, top_db=10)

    #create audio
    above_10 = np.zeros(audio.shape)

    for i in inter_10:
      start,end = i
      above_10[start:end]=audio[start:end]
      sf.write('Output.wav',above_10,sr)
   

"""  # Load the file
    data ,rate = librosa.load ("Noisy_output.wav")
    print("Removing Noise....")
    # Perform Noise Reduction
    reduced_noise = nr.reduce_noise (y=data ,sr=rate )
  
    # Saving file as output.wav
    write ("output.wav", rate , reduced_noise)
    print("Noise is removed...")
    print("Done !")  """
    
def convert():
    # Default arguement values
    sr = 22050
    TRACK_DURATION = 5 # measured in seconds
    SAMPLES_PER_TRACK = sr * TRACK_DURATION
    num_seg=5
    samples_per_segment = int(SAMPLES_PER_TRACK / num_seg)
    
    # Path of saved audio in record function
    audio_path = 'Output.wav'
    
    # Loading audio file in the form of array
    x, sr = librosa.load(audio_path, sr=sr )
    
    # Extracting 5sec array from x and converting into mfccs
    for d in range(num_seg):
     start = samples_per_segment * d
     finish = start + samples_per_segment
     mfccs = librosa.feature.mfcc(y=x[start:finish], n_mfcc=13 ,sr=sr, n_fft=2048, hop_length=512)
     mfccs = mfccs.T
    # print("Output MFCCS : \n",mfccs)
   
    # Converting 3D mfccs (None,44,13) into 4D mfccs (None,44,13,1) 
    mfccs = mfccs[...,np.newaxis]
    print("MFCCs Done_!")    
    # Returning mfccs to calling function
    return(mfccs)

def send_msg(msg) :
    account_sid = 'Ur Id'
    auth_token = 'Ur tocken'
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body=msg,
            from_='Ur Twilio no',
             to='Ur No'
     )


    print(message.sid)
    

def predict(model, X ):
    
    # add a dimension to input data for sample - model.predict() expects a 4d array in this case
    X = X[np.newaxis, ...] # array shape (1, 130, 13, 1)

    # perform prediction
    prediction = model.predict(X)

    # get index with max value
    predicted_index = np.argmax(prediction, axis=1)
    
    # Pedict the label of input audio
    print("Predicted label: {}".format(predicted_index))
    
    # Predict the Class of the label
    if   (predicted_index == 0)  : 
        print("Predicted class : Axe")
        send_msg('Tree is being cut using Axe')
              
    elif (predicted_index == 1)  : 
        print("Predicted class : Chainsaw")
        send_msg('Tree is being cut using Chainsaw')
        
    elif (predicted_index == 2)  : 
        print("Predicted class : Noise")
       # send_msg('Noise')
       
    elif (predicted_index == 3)  :
        print("Predicted class : Random_Sounds")
        #send_msg('Random_Sounds')
        
    elif (predicted_index == 4)  : 
        print("Predicted class : Tree_Falling")
        send_msg('Tree is Falling')
        
    else : 
        print("Nothing....!!") 
        #send_msg('Nothing')
   

if __name__ =="__main__":   
  #while True:
     # Removing saved .wav file from device  
    os.remove('Noisy_output.wav')           
    os.remove('Output.wav') 
    # Function call to Record the audio in .wav file.      
    record()                     
    # Function call to Convert recorded audio into MFCCs and to return the MFCCs.
    mfccs=convert()              
    # Function call to Predict the class based on the Input MFCCs.
    predict(model,mfccs)          
    # Adding 2 sec delay
    # time.sleep(2)    
    # print("Press m to exit---")  
    #time.sleep(2)
    # Detect the pressed key if == m , break out of the loop
    #if keyboard.is_pressed("m"):  
       # print(" m key is  pressed !!")
       # break
        
#print("Out of the loop !!")

