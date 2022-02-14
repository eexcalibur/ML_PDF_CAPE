include=/global/common/software/m2136/conda/envs/tensorflow/include/python3.10
libs=/global/common/software/m2136/conda/envs/tensorflow/lib
#export PYTHONPATH=/global/homes/z/zhangtao/fortran-call-python/fortran_call_python

gcc -g  -o  cape_ml_bridge  cape_ml_bridge.c -I${include}   -Wl,-rpath ${libs} -L${libs} -lpython3.10
