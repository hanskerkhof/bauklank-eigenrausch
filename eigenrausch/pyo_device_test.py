from pyo import Server, Sine, pa_list_devices, pa_get_default_output

# List devices (printed to the console)
print("Audio devices:")
pa_list_devices()

# Get default output device index (according to PortAudio)
default_out = pa_get_default_output()
print(f"\nDefault output device index: {default_out}\n")

# Choose which device index to use.
# Start with the default; you can change this to another index after seeing the list.
output_index = default_out

print(f"Using output device index: {output_index}\n")

# Create server, set output device, then boot.
s = Server(duplex=0)   # output only is fine
s.setOutputDevice(output_index)
s.boot()
s.start()

# Simple, clearly audible tone.
tone = Sine(freq=440, mul=0.1).out()

try:
    input("Playing test tone. Press Enter to stop...\n")
except KeyboardInterrupt:
    pass
finally:
    s.stop()
    s.shutdown()
