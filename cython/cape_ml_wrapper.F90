#define blk 12
#define lev 72

module cape_ml_wrapper
    interface
    real (C_DOUBLE) function cape_ml_c(t,p,q, cape)  bind(C, name="cape_ml")
        use iso_c_binding
        implicit none

        real (C_DOUBLE)  :: t(blk,lev)
        real (C_DOUBLE)  :: p(blk,lev)
        real (C_DOUBLE)  :: q(blk,lev)
        real (C_DOUBLE)  :: cape(blk)

    end function cape_ml_c
    end interface
end module cape_ml_wrapper
     
