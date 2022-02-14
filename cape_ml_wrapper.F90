module cape_ml_wrapper
    interface
    real (C_DOUBLE) function cape_ml_c(t,p,q) bind(C, name="cape_ml")
        use iso_c_binding
        implicit none
        real (C_DOUBLE) ::  t(72)
        real (C_DOUBLE) ::  p(72)
        real (C_DOUBLE) ::  q(72)
    end function cape_ml_c
    end interface
end module cape_ml_wrapper
     
