#include <assert.h>

int main() {
    int offset;
    offset = 0x80000000;
    assert(0x0000000F /* 15 */ > *((int*)0x00020200 + offset));
    *((int*)0x00020200 + offset) = 0xF /* 15 */;
}