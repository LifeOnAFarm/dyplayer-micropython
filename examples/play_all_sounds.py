from machine import UART, Pin
import time
from dyplayer import DYPlayer

# Initialize the DYPlayer instance
# Replace with the appropriate UART ID and pin numbers for your setup
uart_id = 0  # Example UART ID
tx_pin_number = 0  # Example TX pin number
rx_pin_number = 1  # Example RX pin number
player = DYPlayer(uart_id, tx=tx_pin_number, rx=rx_pin_number)

def setup():
    # Set the volume to 15 (out of a range, assuming 0-30 for 50%)
    player.set_volume(15)

    # Set cycle mode to repeat (play all and repeat)
    player.set_cycle_mode(DYPlayer.PlayMode.Repeat)

    # Start playing
    player.play()

def loop():
    time.sleep(5)  # Delay for 5 seconds

# Run the setup
setup()

# Main loop
while True:
    loop()