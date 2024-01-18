import math


def raman_wl(J, las_wl):
    wl_scat = 1/((1/las_wl) + B_0 * (4 * J - 2))
    const = gamma_squared * 64 * math.pi**4 / 45
    ram_sec = const * 3 * J * (J - 1) / (2 * (2*J + 1) * (2*J - 1) * wl_scat**4)
    #print(wl_scat*1E9, ram_sec)
    return wl_scat*1E9, ram_sec


def population(J, A):
    if J % 2 == 0:
        F = A **(-1) * 3 * (2 * J + 1) * exp ** (-exp_coef * J * (J + 1))
    else:
        F = A **(-1) * 6 * (2 * J + 1) * exp ** (-exp_coef * J * (J + 1))
    return F


gamma_squared = 0.51E-60  # m^6
B_0 = 198.96  #m^-1
las_wl = 1064.4E-9  # m

k_bolt = 1.38E-23  #J/K
h_plank = 6.63E-34
c = 3E8
exp = 2.718

T = 19.9 + 273.15  #K
p_torr = 80   #Pa for 80 Torr
p_pascal = p_torr * 133.3
E_las = 1  #J
scat_length = 15E-3
omega_scat = 1E-3
detector_eff = 0.45   #around 45% at 1.064

n = p_torr / (k_bolt * T)
exp_coef = h_plank * c * B_0 / (k_bolt * T)

ph_coef = n * E_las * las_wl / (h_plank * c)
geom_coef = scat_length * omega_scat


A = 0
for j in range(40):
    if j % 2 == 0:
        A += 3 * (2 * j + 1) * exp**(-exp_coef * j * (j+1))
    else:
        A += 6 * (2 * j + 1) * exp ** (-exp_coef * j * (j + 1))


section = []
popul = []

for k in range(2, 42):
    section.append(raman_wl(k, las_wl))
    popul.append(population(k, A))

for i in range(len(section)):
    #print(section[i][0], section[i][1] * popul[i] * ph_coef * geom_coef )
    print(section[i][0], section[i][1] * popul[i])
    #print(section[i][0], section[i][1] )