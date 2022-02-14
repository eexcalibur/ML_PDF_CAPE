#include <stdio.h>
#include <Python.h>

#define lev 72

double
call_python(char *pyname, char *funname, double args[], int N)
{
    PyObject *pName, *pModule, *pFunc;
    PyObject *pArgs, *pValue;
    int i;

    Py_Initialize();
    Py_SetPath("/global/cscratch1/sd/zhangtao/E3SM/SCM_runs/e3sm_scm_ARM97/case_scripts/SourceMods/src.eam/");
    //printf("%s\n", Py_GetPath());
    PyRun_SimpleString("import sys\nsys.path.append('/global/cscratch1/sd/zhangtao/E3SM/SCM_runs/e3sm_scm_ARM97/case_scripts/SourceMods/src.eam/')");
    pName = PyUnicode_DecodeFSDefault(pyname);
    /* Error checking of pName left out */

    pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    if (pModule != NULL) {
        pFunc = PyObject_GetAttrString(pModule, funname);
        /* pFunc is a new reference */

        if (pFunc && PyCallable_Check(pFunc)) {
            pArgs = PyTuple_New(N);
            for (i = 0; i < N; ++i) {
                //pValue = PyLong_FromLong(args[i]);
                pValue = PyFloat_FromDouble(args[i]);
                if (!pValue) {
                    Py_DECREF(pArgs);
                    Py_DECREF(pModule);
                    fprintf(stderr, "Cannot convert argument\n");
                    exit(EXIT_FAILURE);
                }
                /* pValue reference stolen here: */
                PyTuple_SetItem(pArgs, i, pValue);
            }
            pValue = PyObject_CallObject(pFunc, pArgs);
            Py_DECREF(pArgs);
            if (pValue != NULL) {
                printf("Result of call: %f\n", PyFloat_AsDouble(pValue));
                //Py_DECREF(pValue);
            }
            else {
                Py_DECREF(pFunc);
                Py_DECREF(pModule);
                PyErr_Print();
                fprintf(stderr,"Call failed\n");
                exit(EXIT_FAILURE);
            }
        }
        else {
            if (PyErr_Occurred())
                PyErr_Print();
            fprintf(stderr, "Cannot find function \"%s\"\n", funname);
        }
        Py_XDECREF(pFunc);
        Py_DECREF(pModule);
    }
    else {
        PyErr_Print();
        fprintf(stderr, "Failed to load \"%s\"\n", pyname);
        exit(EXIT_FAILURE);
    }
    //if (Py_FinalizeEx() < 0) {
    //    exit(EXIT_FAILURE);
   // }
    return PyFloat_AsDouble(pValue);
}

double
cape_ml(double t[], double p[], double q[])
{
    double cape_pdf;
    int i;
    //char *pyname = "cape_pdf";
    //char *funname = "trigger";
    char *pyname = "6_example_use_of_ml_pdf_cape";
    char *funname = "main";
    double args[lev*3];

    for (i = 0; i < lev; i++){
        args[i] = t[i];
        args[lev+i] = p[i];
        args[lev*2+i] = q[i];
    }

    cape_pdf = call_python(pyname, funname, args, lev*3);

    return cape_pdf;
}
    
/*
int
main(int argn, char **argv)
{
    double cape_pdf;
    double t[5] = {1,2,3,4,5};
    double p[5] = {1,2,3,4,5};
    double q[5] = {1,2,3,4,5};

    cape_pdf = cape_ml(t,p,q);
    return 0;
}
*/
