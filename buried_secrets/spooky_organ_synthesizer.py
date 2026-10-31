"""
Spooky Organ & Theremin Synthesizer
Vintage audio routine written for the 1999 Halloween demo scene.
Buried alive in Git history!
"""
import math

def play_phantom_chord(frequency_hz: float = 440.0, duration_sec: float = 1.5) -> str:
    """Generates eerie pipe organ harmonics."""
    samples = []
    sample_rate = 44100
    total_samples = int(sample_rate * duration_sec)
    for i in range(total_samples):
        t = i / sample_rate
        # Fundamental + spooky minor thirds & detuned fifths
        wave = (
            0.5 * math.sin(2 * math.pi * frequency_hz * t) +
            0.3 * math.sin(2 * math.pi * (frequency_hz * 1.2) * t) +
            0.2 * math.sin(2 * math.pi * (frequency_hz * 1.5) * t)
        )
        samples.append(wave)
    return f"[Phantom Sound] Synthesized {len(samples)} eerie audio samples at {frequency_hz} Hz!"

def summon_the_dead():
    return "IT LIVES! The 1999 Spooky Organ has been raised from the graveyard!"

if __name__ == "__main__":
    print(summon_the_dead())
    print(play_phantom_chord(330.0))
