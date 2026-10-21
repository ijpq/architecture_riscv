/* Environment smoke test only: legal victim calls, no speculative attack. */
#include <stdint.h>
#include <stdio.h>

static long leak(size_t index, int shift)
{
    register long a0 __asm__("a0") = (long)index;
    register long a1 __asm__("a1") = shift;
    register long a7 __asm__("a7") = 101;
    __asm__ volatile ("ecall" : "+r"(a0) : "r"(a1), "r"(a7) : "memory");
    return a0;
}

int main(void)
{
    long first = leak(0, 0);
    long last = leak(127, 7);
    long invalid = leak(128, 0);
    if (first < 0 || first > 255 || last < 0 || last > 255 || invalid != -1) {
        printf("CS152_PK_VICTIM_FAIL legal=%ld,%ld invalid=%ld\n", first, last, invalid);
        return 1;
    }
    puts("CS152_PK_VICTIM_PASS syscall=101 legal-bounds-and-rejection");
    return 0;
}
