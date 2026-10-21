/* Infrastructure self-check, not a solution to any course vector kernel. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

void setStats(int enable);
unsigned long rvv_probe(const uint32_t *source, uint32_t *destination);

int main(int argc, char **argv)
{
    uint32_t source[32] __attribute__((aligned(64)));
    uint32_t destination[32] __attribute__((aligned(64))) = {0};
    for (unsigned i = 0; i < 32; ++i)
        source[i] = i + 1;
    setStats(1);
    unsigned long vl = rvv_probe(source, destination);
    setStats(0);
    if (vl == 0 || vl > 32)
        return 1;
    if (argc != 2 || vl * 32 != strtoul(argv[1], 0, 10))
        return 2;
    for (unsigned i = 0; i < vl; ++i)
        if (destination[i] != source[i] + 128)
            return 3;
    printf("CS152_RVV_RUNTIME_PASS vlen=%lu elements_checked=%lu\n", vl * 32, vl);
    return 0;
}
