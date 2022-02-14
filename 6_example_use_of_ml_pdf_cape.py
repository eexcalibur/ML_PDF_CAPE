#!/usr/bin/env python	
#
# Cyril J Morcrette (2021), Met Office, UK
#
# In Met Office, use "module load scitools/experimental-current" at the command line before running this.
#
# Code for 
#
# Import some modules (possibly more than are strictly needed, but I did not remove what was not needed).

import numpy as np
#import iris
#import matplotlib.pyplot as plt
#import netCDF4 as nc
import tensorflow as tf
#import warnings

from tensorflow import keras
from keras.models import model_from_json
import sys

def main(*args):
    #
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
    n_bins     = 32

    temp = np.array(args[:nz])
    pres = np.array(args[nz:2*nz])
    qv = np.array(args[2*nz:])


    #
    # Read in data in physical units
    #filein=gcm_string+'_example_t.dat'
    #temp=np.loadtxt(filein)
    #filein=gcm_string+'_example_q.dat'
    #qv=np.loadtxt(filein)
    #filein=gcm_string+'_example_p.dat'
    #pres=np.loadtxt(filein)

    #
    # Apply 1st simple (global) normalisation
    max_temp  = 320.0
    min_temp  = 140.0
    max_qv    = 0.025
    max_pres  = 106000.0
    temp      = ( temp - min_temp) / (max_temp-min_temp)
    qv        = qv / max_qv
    pres      = pres / max_pres
    # Read in level-by-level means and standard deviation (one long vector containing data for t, q and p).

    file_path = "/global/cscratch1/sd/zhangtao/E3SM/SCM_runs/e3sm_scm_ARM97/case_scripts/SourceMods/src.eam/"
    filein    = file_path+gcm_string+'_ml_pdf_cape_mean.dat'
    means     = np.loadtxt(filein)
    filein    = file_path+gcm_string+'_ml_pdf_cape_std.dat'
    stds      = np.loadtxt(filein)
    #
    temp_mean = means[   0:  nz]
    qv_mean   = means[  nz:2*nz]
    pres_mean = means[2*nz:3*nz]
    #
    temp_std  = stds[   0:  nz]
    qv_std    = stds[  nz:2*nz]
    pres_std  = stds[2*nz:3*nz]
    # Do 2nd normalisation
    for k in np.arange(0,nz):
        if temp_std[k] > 0.0:
            temp[k]=(temp[k]-temp_mean[k])/temp_std[k]
        else:
            temp[k]=temp[k]-temp_mean[k]
        if qv_std[k] > 0.0:
            qv[k]=(qv[k]-qv_mean[k])/qv_std[k]
        else:
            qv[k]=qv[k]-qv_mean[k]
        if pres_std[k] > 0.0:
            pres[k]=(pres[k]-pres_mean[k])/pres_std[k]
        else:
            pres[k]=pres[k]-pres_mean[k]
    #
    # Define arrays of correct size for passing into ML
    tqp_data=np.empty([2,nz,n_channels])
    extra_data=np.empty([2,1,n_scalars])
    # Put temp, qv and pressure into the 3 channels
    tqp_data[0,:,0] = temp
    tqp_data[0,:,1] = qv
    tqp_data[0,:,2] = pres
    # As ML algo expects to deal with lots of sample, it complains when it only has one, 
    # (so just replicate that one entry).
    tqp_data[1,:,:] = tqp_data[0,:,:]

    # Now deal with 4 scalar inputs    
    max_orog          = 4000.0
    # Specify an altitude of 100m (normalised by 4000)
    extra_data[0,:,0] = 100.0 / max_orog
    # Specify a std of orography of 50m (normalised by 1200)
    extra_data[0,:,1] = 50.0 / 1200.0
    # Specify the land-sea mask, i.e. fraction of the grid-box that is land (let's say 80% land : 20% sea in this example)
    extra_data[0,:,2] = 0.8
    # Specify a gridbox size (normalised by 144km, i.e. 1 for dx=144km, 0.5 for dx=72km, 0.347 for 50 km.
    extra_data[0,:,3] = 0.347
    # Replicate that entry.
    extra_data[1,:,:] = extra_data[0,:,:]

    # Read in the details of the machine learning model (i.e. number of layer and nodes etc).
    # This was written out by 4_ml_pdf_cape.py
    json_file         = open(file_path+gcm_string+'_ML_PDF_CAPE.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model             = model_from_json(loaded_model_json)

    # Now read in the most recent weights saved when training that model.
    model.load_weights(file_path+gcm_string+'_ML_PDF_CAPE.h5')
    #model.load_weights(file_path+gcm_string+'_ML_PDF_CAPE_trained_on_31_days.h5')

    predy = model.predict([tqp_data, extra_data])

    # This should have size (number of samples, number of bins)
    print('predy.shape=',predy.shape)

    # The output from the ML code is the PDF of CAPE. Take the first (and only) here example
    pdf_of_cape = predy[0,:]

    x           = np.arange(0,n_bins)

    # This plots the PDF as a function of the bin number
    #plt.figure()
    #plt.plot(x,pdf_of_cape)
    #plt.savefig("1_pdf_of_cape.png")
    #plt.show()


    max_cape    = 4500
    cape_array  = (x**2.0)*max_cape/((n_bins-1)*(n_bins-1))

    # The expectation value, basically the mean value of CAPE is:
    expectation_value = np.sum( cape_array * pdf_of_cape )

    return expectation_value
    # This plots the PDF as a function of the value of CAPE
    # and plots the mean value (expectation value).
#    plt.figure()
#    plt.plot(cape_array,pdf_of_cape,'k-')
#    plt.plot([expectation_value,expectation_value],[0,0.125],'r--')
#    plt.show()
#
#
#    # The cumulative distribution function (CDF) is found by integrating the PDF.
#    cdf_of_cape=np.cumsum(pdf_of_cape)
#
#    # If we then select a number at random between 0 and 1
#    rand_number=np.random.rand(1,1)[0,0]
#
#    # And interpolate to find the value of CAPE at that random location in the CDF
#    cape=np.interp(rand_number,cdf_of_cape,cape_array)
#
#    # This plots the CDF as a function of the value of CAPE 
#    # and shows how random number allows a value to be taken from the CDF.
#    plt.figure()
#    plt.plot(cape_array,cdf_of_cape,'k-')
#    plt.plot([0,cape],[rand_number,rand_number],'g--')
#    plt.plot([cape,cape],[rand_number,0],'b:')
#    plt.show()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    main()
