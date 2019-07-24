
from math import ceil

p = print


def mod3(a, r=13, t=14, c=15):
    # r = (a >> 8) + (a & 0xff); // r mod 255 == a mod 255
    p("vpsrlw $8, %ymm{}, %ymm{}".format(a, r))
    p("vpand mask_ff, %ymm{}, %ymm{}".format(a, a))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 4) + (r & 0xf); // r' mod 15 == r mod 15
    p("vpand mask_f, %ymm{}, %ymm{}".format(r, a))
    p("vpsrlw $4, %ymm{}, %ymm{}".format(r, r))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    for _ in range(2):
        p("vpand mask_3, %ymm{}, %ymm{}".format(r, a))
        p("vpsrlw $2, %ymm{}, %ymm{}".format(r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    #   t = r - 3;
    p("vpsubw mask_3, %ymm{}, %ymm{}".format(r, t))
    #   c = t >> 15;  t is signed, so shift arithmetic
    p("vpsraw $15, %ymm{}, %ymm{}".format(t, c))

    tmp = a
    #   return (c&r) ^ (~c&t);
    p("vpandn %ymm{}, %ymm{}, %ymm{}".format(t, c, tmp))
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(c, r, t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, tmp, r))


if __name__ == '__main__':
    p(".data")
    p(".align 32")

    p("const_3_repeating:")
    for i in range(16):
        p(".word 0x3")

    p("shuf_b8_to_low_doubleword:")
    for j in range(16):
        p(".byte 8")
        p(".byte 255")

    p("mask_ff:")
    for i in range(16):
        p(".word 0xff")

    p("mask_f:")
    for i in range(16):
        p(".word 0xf")
    p("mask_3:")
    for i in range(16):
        p(".word 0x03")

    p(".text")
    p(".global mod_3_pass")
    p(".att_syntax prefix")

    p("mod_3_pass:")

    input = 0
    output = 1

    for i in range(ceil(509 / 16)):
        p("vmovdqa {}(%rsi), %ymm{}".format(i*32, input))
        mod3(input, output)
        p("vmovdqa %ymm{}, {}(%rdi)".format(output, i*32))

    p("ret")
