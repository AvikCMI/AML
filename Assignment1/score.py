# -*- coding: utf-8 -*-
"""score.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IbHEAChghAKclT5lSzv-NhqAbCYoaohq
"""

import joblib
import sklearn
import pandas as pd
from train import data_prep
filename = "best_model.joblib"
best_model = joblib.load(filename)

def score(text:str, model, threshold:float):
    k = {'message': [text]}
    testing_data = pd.DataFrame(k)
    te_d,te_i,te_c = data_prep(testing_data)
    testing_X = pd.DataFrame(data = te_d, 
                    index = te_i, 
                    columns = te_c)
    propensity = ((model.predict_proba(testing_X)).tolist())[0][1]
    if propensity >= threshold:
        prediction = 1
    else:
        prediction = 0
    return prediction, propensity

l = ["Hi, the SEXYCHAT girls are waiting for you to text them. Text now for a great night chatting. send STOP to stop this service", "Wait for 5 mins, I'm coming!","call this number, you will get reward. Don't miss the opportunity."]
threshold_list = [0,0.1,0.3,0.5,0.7,0.9,1]

f = open("output.txt", "w")
for i in threshold_list:
    for j in l:
        s = score(j, best_model, i)
        L = ["sentence: ",j,"\t","threshold: ",str(i),'\t',"(prediction & propensity): ",str(s),"\n"]
        f.writelines(L) 
f.close()