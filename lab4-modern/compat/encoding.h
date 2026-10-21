/* Compatibility for unused course util.h stats helpers in user-mode Linux.
 * These are real user-readable counters, not fabricated performance results.
 * Published measurements use gem5's bracketed ROI statistics instead. */
#ifndef CS152_SE_ENCODING_H
#define CS152_SE_ENCODING_H
#define CS152_CSR_mcycle "cycle"
#define CS152_CSR_minstret "instret"
#define read_csr(reg) ({ unsigned long value; \
    __asm__ volatile ("csrr %0, " CS152_CSR_##reg : "=r" (value) :: "memory"); value; })
#endif
