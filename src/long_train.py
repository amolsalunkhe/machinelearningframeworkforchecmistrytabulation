"""
Created on Wed Aug  4 17:50:06 2021

@author: amol
"""

# set TF GPU memory growth so that it doesn't hog everything at once
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

from main import *

# util for getting objects' fields' names
field_names = lambda x: list(vars(x).keys())

#Prepare the DataFrame that will be used downstream
dp = DataPreparer()
dp.createPCAs()
dp.sparsePCAs()
dp.zmixOrthogonalPCAs()
df = dp.getDataframe()

# TODO: add PCA from linear model first
df.to_csv('PCA_data.csv', index=False)

# currently passing dp eventually we want to abstract all the constants into 1 class
dm = DataManager(df, dp)

""" prepare PCDNNV2 for loading (from prior experiments) """
exprExec = PCDNNV2ExperimentExecutor()
exprExec.setModelFactory(PCDNNV2ModelFactory())

dataType = 'randomequaltraintestsplit' #'frameworkincludedtrainexcludedtest'
inputType = 'AllSpecies'
dataSetMethod = f'{inputType}_{dataType}'
opscaler = 'PositiveLogNormal' #"MinMaxScaler"
ZmixPresent = 'Y'
concatenateZmix = 'Y'
kernel_constraint = 'N'
kernel_regularizer = 'N'
activity_regularizer = 'N'
noOfCpv = 4
noOfNeurons = 53

exprExec.modelFactory.loss='mse'
exprExec.modelFactory.activation_func='relu'
exprExec.modelFactory.width=1024
exprExec.modelFactory.dropout_rate=0.5
exprExec.debug_mode = False
exprExec.batch_size = 512
exprExec.epochs_override = 20000
exprExec.n_models_override = 1

# initialize experiment executor...
exprExec.dm = dm
exprExec.df_experimentTracker = pd.DataFrame()
exprExec.modelType = 'PCDNNV2'

history = exprExec.executeSingleExperiment(noOfNeurons,dataSetMethod,dataType,inputType,ZmixPresent,noOfCpv,concatenateZmix,kernel_constraint,
                                           kernel_regularizer,activity_regularizer,opscaler=opscaler)

import matplotlib.pyplot as plt

#  "Accuracy"
plt.plot(history.history['R2'])
plt.plot(history.history['val_R2'])
plt.title('model R2 history')
plt.ylabel('R2')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.savefig('long_train_R2.png')