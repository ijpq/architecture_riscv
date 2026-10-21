/* A fixed dependent instruction chain for checking RVV execution/FU latency.
 * No course kernel is implemented here. Vector registers are caller-saved. */
.text
.align 2
.global rvv_probe
.type rvv_probe, @function
rvv_probe:
    vsetvli t0, zero, e32, m1, tu, mu
    vle32.v v8, (a0)
    .rept 128
        vadd.vi v8, v8, 1
    .endr
    vse32.v v8, (a1)
    mv a0, t0
    ret
.size rvv_probe, .-rvv_probe
.section .note.GNU-stack,"",@progbits
