import os
from wavebender import sine_wave, compute_samples, write_wavefile

def test_finite_wave_generation():
    framerate = 44100
    duration = 1
    nframes = framerate * duration

    channels = ((sine_wave(440.0, framerate=framerate, amplitude=0.5),),)

    samples = compute_samples(channels, nframes)

    filename = 'test_output.wav'
    if os.path.exists(filename):
        os.remove(filename)

    try:
        with open(filename, 'wb') as f:
            write_wavefile(f, samples, nframes, nchannels=1, framerate=framerate)

        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"SUCCESS: {filename} created. Size: {size} bytes.")
        else:
            print(f"FAILURE: {filename} not created.")

    except Exception as e:
        print(f"FAILURE: Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_finite_wave_generation()
