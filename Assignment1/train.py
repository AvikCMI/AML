# -*- coding: utf-8 -*-
"""train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/AvikCMI/AML/blob/main/Assignment1/train.ipynb
"""

# Commented out IPython magic to ensure Python compatibility.
# Python ≥3.5 is required
import sys
assert sys.version_info >= (3, 5)

# Scikit-Learn ≥0.20 is required
import sklearn
assert sklearn.__version__ >= "0.20"

# Common imports
import numpy as np
import os
import pandas as pd
# For visualization
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
pd.options.display.max_rows = None
pd.options.display.max_columns = None

# to make this notebook's output stable across runs
np.random.seed(42)

# To plot pretty figures
# %matplotlib inline
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rc('axes', labelsize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)

# Where to save the figures
PROJECT_ROOT_DIR = "."
CHAPTER_ID = "decision_trees"
IMAGES_PATH = os.path.join(PROJECT_ROOT_DIR, "images", CHAPTER_ID)
os.makedirs(IMAGES_PATH, exist_ok=True)

def save_fig(fig_id, tight_layout=True, fig_extension="png", resolution=300):
    path = os.path.join(IMAGES_PATH, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)

# Common imports
import numpy as np
import os
from urllib.parse import urlparse

# ML flow imports
import mlflow
import mlflow.sklearn

import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

!pip install mlflow

from sklearn.metrics._plot.precision_recall_curve import precision_recall_curve
from sklearn.metrics import auc
def eval_metrics(actual, pred):
    prec, recall,_ = precision_recall_curve(actual, pred)
    aucpr = auc(recall, prec)
    return aucpr

"""### Loading the train, test, validation data:"""

train_data = pd.read_csv('train.csv')
test_data = pd.read_csv('test.csv')
valid_data = pd.read_csv('validation.csv')

"""### Postprocessing data for transforming message to vector"""

spam_words = {}
ham_words = {}
s_c = 0
h_c = 0
i = 0
for line in list(train_data.message):
    if list(train_data.label)[i] == "spam":
        s_c += 1
        s_w = line.split(" ")
        for word in s_w:
            if word.lower() in spam_words.keys():
                spam_words[word.lower()] += 1
            else:
                spam_words[word.lower()] = 1
    else:
        h_c += 1
        h_w = line.split(" ")
        for word in h_w:
            if word.lower() in ham_words.keys():
                ham_words[word.lower()] += 1
            else:
                ham_words[word.lower()] = 1
    i += 1

print(len(spam_words.keys()))

print(h_c,s_c)

ham_words["week"]

spam_words_sorted = sorted(spam_words.items(), key=lambda x:x[1])
spam_words_sorted[0][0]

top_300_spam_words = list(spam_words_sorted[i][0] for i in range(-300,0))
print(top_300_spam_words)

ham_words_sorted = sorted(ham_words.items(), key=lambda x:x[1])
ham_words_sorted[0][0]

top_200_ham_words = list(ham_words_sorted[i][0] for i in range(-200,0))
print(top_200_ham_words)

true_spam_words = []
for i in top_300_spam_words:
    if i in ham_words.keys():
        if ham_words[i] <= h_c/100: #i.e., these spam words appeared very fewer times in ham messages.
            true_spam_words.append(i)
    else:
        true_spam_words.append(i)
print(true_spam_words,len(true_spam_words))

"""So, 90 words were some common words in English which appear frequently in any kind of messages."""

spam_dict = {spam_w: true_spam_words.index(spam_w) for spam_w in true_spam_words}
print(spam_dict)

"""### Message to vector transformation:

Defining function to convert every messages to some vectors to make our training dataset to be fitted to ML models
"""

def messtovec(message):
    data = [0 for i in range(211)] #for 210 spam words, length of message
    content = message.split(" ")
    for i in content:
        if i.lower() in spam_dict.keys():
            data[spam_dict[i.lower()]] = 1
    data[-1] = len(content)
    return data

def data_prep(data):
    column_names = [i for i in true_spam_words] + ["length"]
    Full_data = []
    i = 0
    index_names = []
    for line in list(data.message):
        i += 1
        index_names.append(i)
        d = messtovec(line)
        Full_data.append(d)
    return Full_data,index_names,column_names

tr_d,tr_i,tr_c = data_prep(train_data)
train_X = pd.DataFrame(data = tr_d, 
                  index = tr_i, 
                  columns = tr_c)

va_d,va_i,va_c = data_prep(valid_data)
valid_X = pd.DataFrame(data = va_d, 
                  index = va_i, 
                  columns = va_c)

te_d,te_i,te_c = data_prep(test_data)
test_X = pd.DataFrame(data = te_d, 
                  index = te_i, 
                  columns = te_c)

train_Y = pd.DataFrame(data = list(train_data.label), 
                  index = [i+1 for i in range(len(list(train_data.label)))],
                  columns = ["label"])

test_Y = pd.DataFrame(data = list(test_data.label), 
                  index = [i+1 for i in range(len(list(test_data.label)))],
                  columns = ["label"])

valid_Y = pd.DataFrame(data = list(valid_data.label), 
                  index = [i+1 for i in range(len(list(valid_data.label)))],
                  columns = ["label"])

train_Y['label'] = train_Y['label'].replace(['spam'], 1)
train_Y['label'] = train_Y['label'].replace(['ham'], 0)

test_Y['label'] = test_Y['label'].replace(['spam'], 1)
test_Y['label'] = test_Y['label'].replace(['ham'], 0)

valid_Y['label'] = valid_Y['label'].replace(['spam'], 1)
valid_Y['label'] = valid_Y['label'].replace(['ham'], 0)

#Pie-Chart of output variable
labels = 'spam', 'ham'
sizes = [train_Y.label[train_Y['label']==1].count(), train_Y.label[train_Y['label']==0].count()]
explode = (0, 0.1)
fig1, ax1 = plt.subplots(figsize=(10, 8))
ax1.pie(sizes,explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90,colors =["tomato","turquoise"] )
ax1.axis('equal')
plt.title("Proportion of the spam & ham messages", size = 20)
plt.show()

"""So, this is a very unbalanced dataset

# Random Forest Classifier:
"""

from sklearn.ensemble import RandomForestClassifier
#for computing Mean Absolute Error
from sklearn.metrics import mean_absolute_error
def score_dataset(X_train, X_valid, y_train, y_valid,i,n):
    model = RandomForestClassifier(n_estimators = n, max_depth = i, random_state = 42, class_weight = {0:13,1:87})
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)

MAE = 1
for i in range(1,30):
    print("MAE:",score_dataset(train_X, valid_X, np.ravel(train_Y), np.ravel(valid_Y),i,100),"max_depth =",i)
    temp = score_dataset(train_X, valid_X, np.ravel(train_Y), np.ravel(valid_Y),i,100) 
    if MAE > temp:
        MAE = temp
        max_depth = i

rf = RandomForestClassifier(n_estimators = 100, random_state = 42, max_depth = max_depth, class_weight = {0:13,1:87})
rf.fit(train_X,np.ravel(train_Y))

# Commented out IPython magic to ensure Python compatibility.
#memory used in fitting the Train data to the model
# %load_ext memory_profiler
from memory_profiler import profile

# %memit rf.fit(train_X,np.ravel(train_Y))

pred_Y = rf.predict(test_X)

#confusion matrix for Decision Tree

from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

f = open("random_forest.txt", "w")

accuracy_score = metrics.accuracy_score(test_Y, pred_Y)

con_matrix = confusion_matrix(test_Y,pred_Y, labels=[0,1])

report_matrix = classification_report(test_Y, pred_Y,labels=[0,1])

L = [str(accuracy_score),"\n\n",str(con_matrix),'\n\n', str(report_matrix)] 
f.writelines(L) 
f.close()

from sklearn.metrics import ConfusionMatrixDisplay
fig = plt.figure()
Disp =ConfusionMatrixDisplay(con_matrix,display_labels=['ham','spam'])
Disp.plot()
plt.savefig("random_forest_confusion_matrix")
plt.close(fig)

print(report_matrix)

with mlflow.start_run():
    Model = RandomForestClassifier(n_estimators = 100, random_state = 42, max_depth = max_depth, class_weight = {0:13,1:87})
    Model.fit(train_X,np.ravel(train_Y))

    predicted_qualities = Model.predict(test_X)

    aucpr = eval_metrics(test_Y, predicted_qualities)

    print("Random Forest Classifier model (Area under Precision_Recall Curve={:f}):".format(aucpr))

    mlflow.log_param("Area under Precision Recall Curve", aucpr)


    tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

    # Model regi
    if tracking_url_type_store != "file":
        mlflow.sklearn.log_model(Model, "model", registered_model_name="Random Forest Classifier")
    else:
        mlflow.sklearn.log_model(Model, "model")

"""# Naive Bayes Classifier:"""

# train a Gaussian Naive Bayes classifier on the training set
from sklearn.metrics import mean_absolute_error
def score_dataset(X_train, X_valid, y_train, y_valid, nb):
    model = nb
    model.fit(X_train, np.ravel(y_train))
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)

from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import ComplementNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import CategoricalNB
# instantiate the model
gnb = GaussianNB()
conb = ComplementNB()
mnb = MultinomialNB()
bnb = BernoulliNB()
# canb = CategoricalNB()
nb = [gnb, conb, mnb, bnb]

MAE = 1
for i in nb:
    print("MAE:",score_dataset(train_X, valid_X, np.ravel(train_Y), np.ravel(valid_Y), i),"naive bayes' model =",i)
    temp = score_dataset(train_X, valid_X, np.ravel(train_Y), np.ravel(valid_Y), i) 
    if MAE > temp:
        MAE = temp
        nb_model = i

# fit the model
nb_model.fit(train_X, np.ravel(train_Y))

# Commented out IPython magic to ensure Python compatibility.
#memory used in fitting the Train data to the model
# %load_ext memory_profiler
from memory_profiler import profile
# %memit bnb.fit(train_X,np.ravel(train_Y))

pred_Y = bnb.predict(test_X)

#confusion matrix for Decision Tree

from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

f = open("Bayes'_tree.txt", "w")

accuracy_score = metrics.accuracy_score(test_Y, pred_Y)

con_matrix = confusion_matrix(test_Y,pred_Y, labels=[0,1])

report_matrix = classification_report(test_Y, pred_Y,labels=[0,1])

L = [str(accuracy_score),"\n\n",str(con_matrix),'\n\n', str(report_matrix)] 
f.writelines(L) 
f.close()

from sklearn.metrics import ConfusionMatrixDisplay

fig = plt.figure()
Disp =ConfusionMatrixDisplay(con_matrix,display_labels=['ham','spam'])
Disp.plot()
plt.savefig("Bayes'_confusion_matrix")
plt.close(fig)

print(report_matrix)

with mlflow.start_run():
    Model = BernoulliNB()
    Model.fit(train_X,np.ravel(train_Y))

    predicted_qualities = Model.predict(test_X)

    aucpr = eval_metrics(test_Y, predicted_qualities)

    print("Naive Bayes Classifier model (Area under Precision_Recall Curve={:f}):".format(aucpr))

    mlflow.log_param("Area under Precision Recall Curve", aucpr)


    tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

    # Model regi
    if tracking_url_type_store != "file":
        mlflow.sklearn.log_model(Model, "model", registered_model_name="Naive Bayes Classifier")
    else:
        mlflow.sklearn.log_model(Model, "model")

"""# SVM Classifier:"""

# train a Support Vector Machine classifier on the training set
from sklearn.svm import SVC 
from sklearn.metrics import mean_absolute_error
def score_dataset(X_train, X_valid, y_train, y_valid, k):
    model = SVC(kernel=k) 
    model.fit(X_train, np.ravel(y_train))
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)

MAE = 1
Kernels = ['linear', 'poly', 'rbf', 'sigmoid']
for i in Kernels:
    print("MAE:",score_dataset(train_X, valid_X, np.ravel(train_Y), np.ravel(valid_Y),i),"kernel =",i)
    temp = score_dataset(train_X, valid_X, np.ravel(train_Y), np.ravel(valid_Y),i) 
    if MAE > temp:
        MAE = temp
        kernel = i

# instantiate the model
clf = SVC(kernel=kernel) 
# fit the model
clf.fit(train_X, np.ravel(train_Y))

# Commented out IPython magic to ensure Python compatibility.
#memory used in fitting the Train data to the model
# %load_ext memory_profiler
from memory_profiler import profile
# %memit clf.fit(train_X,np.ravel(train_Y))

pred_Y = clf.predict(test_X)

#confusion matrix for Decision Tree

from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

f = open("SVM.txt", "w")

accuracy_score = metrics.accuracy_score(test_Y, pred_Y)

con_matrix = confusion_matrix(test_Y,pred_Y, labels=[0,1])

report_matrix = classification_report(test_Y, pred_Y,labels=[0,1])

L = [str(accuracy_score),"\n\n",str(con_matrix),'\n\n', str(report_matrix)] 
f.writelines(L) 
f.close()

from sklearn.metrics import ConfusionMatrixDisplay

fig = plt.figure()
Disp =ConfusionMatrixDisplay(con_matrix,display_labels=['ham','spam'])
Disp.plot()
plt.savefig("SVM_confusion_matrix")
plt.close(fig)

print(report_matrix)

with mlflow.start_run():
    Model = SVC(kernel='linear')
    Model.fit(train_X,np.ravel(train_Y))

    predicted_qualities = Model.predict(test_X)

    aucpr = eval_metrics(test_Y, predicted_qualities)

    print("SVM Classifier model (Area under Precision_Recall Curve={:f}):".format(aucpr))

    mlflow.log_param("Area under Precision Recall Curve", aucpr)


    tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

    # Model regi
    if tracking_url_type_store != "file":
        mlflow.sklearn.log_model(Model, "model", registered_model_name="SVM Classifier")
    else:
        mlflow.sklearn.log_model(Model, "model")

"""Hence, we can observe that we are getting highest accuracy as 98% and largest area under Precision_Recall Curve for the model SVM classifier.
So we can choose SVM classifier as our best model.
"""

import joblib
best_model = clf
filename = "best_model.joblib"
joblib.dump(best_model, filename)