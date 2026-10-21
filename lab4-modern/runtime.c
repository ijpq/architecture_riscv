/* Linux-SE adapter only. Kernels and their original verification stay unchanged. */
#include <stdio.h>
#include <gem5/m5ops.h>

void setStats(int enable)
{
    __asm__ volatile ("" ::: "memory");
    if (enable)
        m5_work_begin(0, 0);
    else
        m5_work_end(0, 0);
    __asm__ volatile ("" ::: "memory");
}

int __real_main(int argc, char **argv);
int __wrap_main(int argc, char **argv)
{
    int code = __real_main(argc, argv);
    /* Linux truncates exit status to 8 bits. Original verify() can return
     * 256, 512, etc.; normalize every nonzero value so it cannot become PASS. */
    printf("CS152_LAB4_CHECK_%s code=%d\n", code == 0 ? "PASS" : "FAIL", code);
    return code == 0 ? 0 : 1;
}
