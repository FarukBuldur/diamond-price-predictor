# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 09:30:19 2020

@author: Faruk.Buldur
"""

import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import os
import pymongo

app = Flask(__name__,template_folder='')
diamond = pickle.load(open('diamond.pkl', 'rb'))

class MongoCredential(Exception):
    pass

mongo_pass = os.environ.get('MONGO_PASS')
if mongo_pass == None:
    # self.logger.error(f'Mongo Tapu Secret Not Properly Passed')
    raise MongoCredential
client = pymongo.MongoClient("mongodb+srv://diamond_user:"+mongo_pass+"@cluster0.hltrk.mongodb.net/", 
                                maxPoolSize=100, 
                                waitQueueTimeoutMS=1, 
                                waitQueueMultiple=1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def resubmit():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = [x for x in request.form.values()]
    final_features = [np.array(int_features)]

    cut_dict = {'Fair'  :   [1,0,0,0,0],
                'Good'  :   [0,1,0,0,0],
                'Very Good':[0,0,1,0,0],
                'Premium' : [0,0,0,1,0],
                'Ideal'  :  [0,0,0,0,1]}
    color_dict = {'J':  [1,0,0,0,0,0,0],
                  'I':  [0,1,0,0,0,0,0],
                  'H':  [0,0,1,0,0,0,0],
                  'G':  [0,0,0,1,0,0,0],
                  'F':  [0,0,0,0,1,0,0],
                  'E':  [0,0,0,0,0,1,0],
                  'D':  [0,0,0,0,0,0,1]}
    clarity_dict = {'I1':[1,0,0,0,0,0,0,0],
                  'SI2': [0,1,0,0,0,0,0,0],
                  'SI1': [0,0,1,0,0,0,0,0],
                  'VS2': [0,0,0,1,0,0,0,0],
                  'VS1': [0,0,0,0,1,0,0,0],
                  'VVS2':[0,0,0,0,0,1,0,0],
                  'VVS1':[0,0,0,0,0,0,1,0],
                  'IF' : [0,0,0,0,0,0,0,1]}

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    if final_features[0][0]=="":
        return render_template('result.html', message='Please don\'t Leave Name Blank')
    elif final_features[0][1]=="":
        return render_template('result.html', message='Please don\'t Leave Mail Blank')
    elif final_features[0][3]=="Choose Diamond Cut":
        return render_template('result.html', message='Please don\'t Leave Diamond Cut Blank')
    elif final_features[0][4]=="Choose Diamond Color":
        return render_template('result.html', message='Please don\'t Leave Diamond Color Blank')
    elif final_features[0][5]=="Choose Diamond Clarity":
        return render_template('result.html', message='Please don\'t Leave Diamond Clarity Blank')
    elif is_number(final_features[0][2])==False:
        return render_template('result.html', message='Please Enter a Valid Carat')
    else:
        carat = float(final_features[0][2])
        cut_dummy = cut_dict[final_features[0][3]]
        color_dummy = color_dict[final_features[0][4]]
        clarity_dummy = clarity_dict[final_features[0][5]]
        diamond_input = [carat] + cut_dummy + clarity_dummy + color_dummy
        prediction = diamond.predict(np.reshape(diamond_input, (1, -1)))

        mail_params = [['Estimated Diamond Price is:  $ {:,.2f}'.format(prediction[0])][0],
        final_features[0][2],final_features[0][3],final_features[0][4],final_features[0][5],final_features[0][6]]

        ### DatabaseSave
        try:
            database_name = "Diamond"
            collection_name_archive = "Queries"
            database = client[database_name]
            prefArchive = database[collection_name_archive]
            #### prefArchive to be populated !!

            prefArchive.insert_one({"User Name":int_features[0], 
                        "Email":int_features[1],
                        "Carat":int_features[2],
                        "Cut": int_features[3],
                        "Color": int_features[4],
                        "Clarity": int_features[5],
                        "Comment": int_features[6],
                        })
        except:
            pass
        
        return render_template('result.html', message='Estimated Diamond Price is $ {:,.2f}'.format(prediction[0]))


if __name__ == "__main__":
    app.run(debug=True)