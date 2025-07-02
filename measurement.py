import libm2k
import numpy as np
import matplotlib.pyplot as plt

# Sweep-Parameter
f_start = 10_000         # 10 kHz
f_stop = 10_000_000      # 10 MHz
n_steps = 150
amplitude = 1.0
sample_rate = 20e6       # Höherer Wert für hohe Frequenzen
n_samples = 4000

frequencies = np.logspace(np.log10(f_start), np.log10(f_stop), n_steps)

def messreihe(label):
    print(f"Starte Messung: {label}")
    amplitudes = []

    for f in frequencies:
        gen.setFrequency(0, f)
        ctx.sync()
        samples = osc.getSamples(0, n_samples)
        voltage = np.array(samples)
        peak_to_peak = np.max(voltage) - np.min(voltage)
        amplitudes.append(peak_to_peak)

    return np.array(amplitudes)

# Verbindung aufbauen
ctx = libm2k.m2kOpen()
if ctx is None:
    raise Exception("ADALM2000 nicht verbunden.")
ctx.calibrateADC()

gen = ctx.getAnalogOut()
osc = ctx.getAnalogIn()
ctx.setTimeout(2.0)

gen.enableChannel(0, True)
gen.setSampleRate(0, sample_rate)
gen.setChannelMode(0, libm2k.ANALOG_OUT_SINE)
gen.setAmplitude(0, amplitude)

osc.enableChannel(0, True)
osc.setSampleRate(sample_rate)
osc.setRange(0, 2.5)

# --- Messung 1: Leermessung (nur Luft)
input("Bitte LEEREN Kondensator einlegen und Enter drücken...")
leer_amplituden = messreihe("Leer")

# --- Messung 2: Befüllt mit Kaffeepulver
input("Jetzt Kaffeepulver einfüllen und Enter drücken...")
kaffee_amplituden = messreihe("Kaffee")

# --- Aufräumen
gen.enableChannel(0, False)
ctx.close()

# --- Analyse
res_index_leer = np.argmax(leer_amplituden)
res_index_kaffee = np.argmax(kaffee_amplituden)

f_res_leer = frequencies[res_index_leer]
f_res_kaffee = frequencies[res_index_kaffee]

# Berechnung bei bekannter Induktivität
L = 1e-3  # 1 mH
C_leer = 1 / ((2 * np.pi * f_res_leer)**2 * L)
C_kaffee = 1 / ((2 * np.pi * f_res_kaffee)**2 * L)

print("\n--- Ergebnisse ---")
print(f"Resonanz leer:    {f_res_leer/1000:.1f} kHz → C = {C_leer*1e12:.2f} pF")
print(f"Resonanz Kaffee:  {f_res_kaffee/1000:.1f} kHz → C = {C_kaffee*1e12:.2f} pF")
print(f"ΔC = {(C_kaffee - C_leer)*1e12:.2f} pF")

# --- Plot
plt.figure(figsize=(10,6))
plt.semilogx(frequencies, leer_amplituden, label='Leer (Luft)', color='blue')
plt.semilogx(frequencies, kaffee_amplituden, label='Kaffee', color='green')
plt.axvline(f_res_leer, color='blue', linestyle='--')
plt.axvline(f_res_kaffee, color='green', linestyle='--')
plt.xlabel("Frequenz (Hz)")
plt.ylabel("Amplitude (Vpp)")
plt.title("Frequenzgang – Leermessung vs. Kaffee")
plt.legend()
plt.grid(True, which='both', ls=':')
plt.tight_layout()
plt.show()
