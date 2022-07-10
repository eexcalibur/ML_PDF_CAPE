#include <stdio.h>
#include <Python.h>
#include "ml_pdf_cape.h"
#include <sys/time.h>

#define lev 72
#define block 12

double
cape_ml(double t[lev][block], double p[lev][block], double q[lev][block], double cape[block])
{
    double *cape_r;
    struct timeval tv1,tv2;
    float runtime;

    PyImport_AppendInittab("ml_pdf_cape", PyInit_ml_pdf_cape);
    Py_Initialize();
    PyImport_ImportModule("ml_pdf_cape");


//    printf("in C old\n");
//    for(int i=0; i < block; i++)
//        printf("%f ", cape[i]);
//    printf("\n");

    gettimeofday(&tv1, NULL);
    cape_r = calc_cape(t,p,q);
    gettimeofday(&tv2, NULL);
    runtime=(tv2.tv_usec - tv1.tv_usec)/1000000 + (tv2.tv_sec - tv1.tv_sec);
    printf("time of calc_cape in C: %.2f \n", runtime);

//    printf("in C new\n");
    for(int i=0; i < block; i++){
//        printf("%f ", cape_r[i]);
        cape[i] = cape_r[i];
    }
//    printf("\n");
    //Py_Finalize();
    return 1.0;
}

//int
//main11(int argn, char **argv)
//{
//    double args[72*3];
//    double *cape;
//
//    PyImport_AppendInittab("ml_pdf_cape", PyInit_ml_pdf_cape);
//    Py_Initialize();
//    PyImport_ImportModule("ml_pdf_cape");
//
//    for(int i=0; i<72*3; i++){
//        args[i] = rand()/(double)RAND_MAX;
//        printf("%f ", args[i]);
//    }
//
//    printf("first arg is %f\n",args[0]);
//    cape = calc_cape(args);
//    
//    printf("cape is %f\n", cape[0]);
//
//    Py_Finalize();
//
//    return 0;
//}
