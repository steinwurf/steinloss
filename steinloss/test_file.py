import bitmath
size = 3800 * 1024

speed = bitmath.Byte(bytes= size).best_prefix()

print(float(speed), type(speed.unit))
