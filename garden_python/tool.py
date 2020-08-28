import numpy as np
import math

# def f(x):
#     return np.power(x, 1/3) if x > 0.008856 else 7.787*x + 0.137931

# def RGB2XYZ(R, G, B):
#     X = 0.412453*R + 0.357580*G + 0.180423*B
#     Y = 0.212671*R + 0.715160*G + 0.072169*B
#     Z = 0.019334*R + 0.119193*G + 0.950227*B
#     return X, Y, Z

# def XYZ2LAB(X, Y, Z):
#     X = x / 0.95047
#     Y = Y / 1.0
#     Z = Z / 1.08883
#     L = 116 * f(Y) - 16
#     A = 500 * (f(X) - f(Y))
#     B = 200 * (f(Y) - f(Z))
#     return L, A, B

# def RGB2LAB(R, G, B):
#     X, Y, Z = RGB2XYZ(R, G, B)
#     L, A, B = XYZ2LAB(X, Y, Z)
#     return L, A, B

def Str2RGB(s):
    R = int(s[0:2], 16)
    G = int(s[2:4], 16)
    B = int(s[4:6], 16)
    return R, G, B

def Chromatic(R1, G1, B1, R2, G2, B2):
    r_mean = (R1 + R2)/2
    R = R1 - R2
    G = G1 - G2
    B = B1 - B2
    return math.sqrt((2+r_mean)/256*(R**2) + 4*(G**2) + (2+(255-r_mean)/256)*(B**2))


# file = open("color.txt", "rb")
# content = file.read()
# content = eval(content)
# file.close()
# print(content)
R1, G1, B1 = Str2RGB("A2E3F4")
R2, G2, B2 = Str2RGB("325FA1")
r = Chromatic(R1, G1, B1, R2, G2, B2)
print(r)
