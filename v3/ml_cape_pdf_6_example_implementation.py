#!/usr/bin/env python	
#
# Cyril J Morcrette (2021), Met Office, UK
#
# In Met Office, use "module load scitools/experimental-current" at the command line before running this.
#
# Code for 
#
# Import some modules

import numpy as np
#import iris
import matplotlib.pyplot as plt
import netCDF4 as nc
import tensorflow as tf
#import warnings

from tensorflow import keras
from keras.models import model_from_json

def main():
    gcm = 2
    #
    if gcm == 1:
        nz         = 70     # If using raw UM data nz=70 (RAT data using L70_80km level set to match the global model). Data is bottom to top.
        gcm_string = 'UM'
    if gcm == 2:
        nz         = 72     # If using UM data regridded for use in E3SM then nz=72, and top is at 60 km. Data is top to bottom.
        gcm_string = 'E3SM'

    n_channels = 3
    n_scalars  = 4
    #    n_bins     = 32


    tqp_data=np.empty([2,nz,n_channels])
    extra_data=np.empty([2,1,n_scalars])

    filein='example_normalised_tqp.txt'
    tqp_data[0,:,:]=np.loadtxt(filein)
    tqp_data[1,:,:]=np.loadtxt(filein)

    filein='example_extra_info.txt'
    extra_data[0,:,:]=np.loadtxt(filein)
    extra_data[1,:,:]=np.loadtxt(filein)

    # Read in the details of the machine learning model (i.e. number of layer and nodes etc).
    # This was written out by 4_ml_pdf_cape.py
    json_file=open(gcm_string+'_ML_PDF_CAPE.json', 'r')
    loaded_model_json=json_file.read()
    json_file.close()
    model=model_from_json(loaded_model_json)

    # Now read in the most recent weights saved when training that model.
    model.load_weights(gcm_string+'_ML_PDF_CAPE.h5')

    predy=model.predict([tqp_data, extra_data])

    print('predy.shape=',predy.shape)

    plt.figure()
    plt.plot(predy[0,:])
    plt.show()



#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
