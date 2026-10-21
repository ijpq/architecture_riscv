/* Environment check, not a branch-predictor or Spectre exercise solution. */
#include <stdio.h>

static unsigned long cycles(void)
{
    unsigned long value;
    __asm__ volatile ("csrr %0, mcycle" : "=r" (value) :: "memory");
    return value;
}

static unsigned long instructions(void)
{
    unsigned long value;
    __asm__ volatile ("csrr %0, minstret" : "=r" (value) :: "memory");
    return value;
}

int main(void)
{
    volatile unsigned long values[2] = {1, 3};
    unsigned long total = 0;
    unsigned long start_cycles = cycles(), start_instructions = instructions();
    for (unsigned i = 0; i < 32; ++i)
        total += values[i & 1];
    unsigned long elapsed = cycles() - start_cycles;
    unsigned long retired = instructions() - start_instructions;
    if (total != 64 || elapsed == 0 || retired == 0) {
        puts("CS152_BOOM_RUNTIME_FAIL");
        return 1;
    }
    printf("CS152_BOOM_RUNTIME_PASS cycles=%lu instret=%lu\n", elapsed, retired);
    return 0;
}
