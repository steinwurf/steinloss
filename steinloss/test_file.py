import bitmath


size = bitmath.Byte(bytes=4026).best_prefix()
print(bitmath.__file__)

print(size.format("{value:.2f} {unit}"))
