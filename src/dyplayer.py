from machine import UART, Pin

class DYPlayer:
    """
    A class to control the DY-SV17F mp3 player module via UART.
    """
    
    # Enumeration-like classes for better readability in method arguments
    class Device:
        Usb = 0x00      # USB Storage device.
        Sd = 0x01       # SD Card.
        Flash = 0x02    # Flash.
        Fail = 0xfe     # Failed to get device.
        NoDevice = 0xff # No storage device.
    
    class PlayState:
        Fail = -1 # UART communication failed.
        Stopped = 0
        Playing = 1
        Paused = 2
    
    class Eq:
        Normal = 0
        Pop = 1
        Rock = 2
        Jazz = 3
        Classic = 4
    
    class PlayMode:
        Repeat = 0      # Play all music in a sequence, and repeat.
        RepeatOne = 1   # Repeat the current song.
        OneOff = 2      # Play the current song and stop.
        Random = 3      # Play random sound file
        RepeatDir = 4   # Repeat current directory.
        RandomDir = 5   # Play random sound file in current directory.
        SequenceDir = 6 # Play all music in a sequence in current directory.
        Sequence = 7    # Play all music in a sequence, and stop.
    
    class PreviousDir:
        FirstSound = 0  # When navigating to the previous dir, play the first sound.
        LastSound = 1   # When navigating to the previous dir, play the last sound.
    
    # Constructor
    def __init__(self, uart_id, tx=0, rx=1, timeout=1000, timeout_char=100, rxbuf = 10):
        """
        Initializes a new DYPlayer instance with specified UART settings for controlling a DY-SV17F MP3 player module or similar device.
        Args:
            uart_id (int): The UART bus ID to use for communication.
            baudrate (int): Set to 9600 for the DY-SV17F MP3 player module.
            bits (int): The number of data bits in each UART character. Set to 8.
            parity: The parity for UART communication. Set to None.
            stop (int): The number of stop bits. Set to 1.
            tx_pin_number (int): The GPIO pin number used for UART transmission (TX).
            rx_pin_number (int): The GPIO pin number used for UART reception (RX).
            timeout (int, optional): The maximum time in milliseconds to wait for the first character. Default is 1000 ms.
            timeout_char (int, optional): The time to wait in milliseconds between characters. Default is 100 ms.
            rxbuf (int, optional): The size of the internal UART RX buffer in bytes. Default is 10.

        """
        self.uart = UART(uart_id, baudrate=9600, bits=8, parity=None, stop=1, tx=Pin(tx), rx=Pin(rx), timeout=timeout, timeout_char=timeout_char, rxbuf=rxbuf)
        self.buffer = bytearray(10)  # Pre-allocate buffer for reading data from UART
    
    # Methods for sending commands to the module
    def send_command(self, data, crc=None):
        """
        Send command to the module with optional CRC for speed.
        """
        self._flush()   # Flush the buffer before sending a new command

        if crc is None:
            crc = self._checksum(data)
        self.serial_write(data)
        self.serial_write(crc)
        while not self.uart.txdone():
            pass        # Wait until transmission is complete
    
    def serial_write(self, data):
        """
        Write data to the UART.
        """
        if isinstance(data, int):
            # If data is a single byte, convert it to a bytearray
            data = bytearray([data])
        self.uart.write(data)
    
    # Methods for reading responses from the module
    def serial_read(self, length):
        """
        Read data from the UART.
        """
        # Read data into the pre-allocated buffer
        self.uart.readinto(self.buffer, length)
    
    def get_response(self, length):
        """
        Get response from the module. Returns False if no response or CRC failed.
        """
        # Ensure the buffer is the correct size
        if len(self.buffer) < length:
            self.buffer = bytearray(length)
        
        self.serial_read(length)

        # Check if buffer has valid data and validate CRC
        if self.buffer and self._validate_crc(self.buffer):
            return self.buffer[:length]  # Return only the relevant part of the buffer
        return False
    
    # Methods for controlling playback
    def play(self):
        """
        Play the current selected song from the start.
        """
        command = bytearray([0xaa, 0x02, 0x00])
        self.send_command(command, 0xac)

    def pause(self):
        """
        Pause the current song.
        """
        command = bytearray([0xaa, 0x03, 0x00])
        self.send_command(command, 0xad)

    def stop(self):
        """
        Stop the current song.
        """
        command = bytearray([0xaa, 0x04, 0x00])
        self.send_command(command, 0xae)

    def previous(self):
        """
        Play the previous song.
        """
        command = bytearray([0xaa, 0x05, 0x00])
        self.send_command(command, 0xaf)

    def next(self):
        """
        Play the next song.
        """
        command = bytearray([0xaa, 0x06, 0x00])
        self.send_command(command, 0xb0)

    def play_specified(self, number):
        """
        Play a sound file by number, number sent as 2 bytes.

        Args:
            number: e.g. `1` for `00001.mp3`.
        """
        command = bytearray([0xaa, 0x07, 0x02, (number >> 8) & 0xff, number & 0xff])
        self.send_command(command)

    def play_specified_device_path(self, device, path):
        """
        Play a sound file by device and path.
        Path may consist of up to 2 nested directories of 8 bytes long and a
        file name of 8 bytes long excluding the extension of 4 bytes long.
        Args:
            device: e.g DYPlayer.Device.Sd
            path: e.g "/00001.mp3"
        """
        self._by_path_command(0x08, device, path)

    def previous_dir(self, song):
        """
        Select previous directory and start playing the first or last song.
        Args:
            song: DYPlayer.PreviousDir.FirstSound or DYPlayer.PreviousDir.LastSound
        """
        if song == self.PreviousDir.LastSound:
            command = bytearray([0xaa, 0x0e, 0x00])
            self.send_command(command, 0xb8)
        else:
            command = bytearray([0xaa, 0x0f, 0x00])
            self.send_command(command, 0xb9)

    def interlude_specified(self, device, number):
        """
        Play an interlude file by device and number.
        Args:
            device: e.g DYPlayer.Device.Sd
            number: e.g. `1` for `00001.mp3`
        """
        command = bytearray([0xaa, 0x0b, 0x03, device, number >> 8, number & 0xff])
        self.send_command(command)

    def interlude_specified_device_path(self, device, path):
        """
        Play an interlude by device and path.
        Args:
            device: e.g DYPlayer.Device.Sd
            path: e.g "/00001.mp3"
        """
        self._by_path_command(0x17, device, path)

    def stop_interlude(self):
        """
        Stop the interlude and continue playing.
        Will also stop the current sound from playing if interlude is not
        active.
        """
        command = bytearray([0xaa, 0x10, 0x00])
        self.send_command(command, 0xba)

    def combination_play(self, sounds, length):
        """
        Combination play allows you to make a playlist of multiple sound files.
        Args:
            sounds: An array of char[2] containing the names of sounds to play in order.
            length: The length of the array.
        """
        if length < 1:
            return
        command = bytearray([0xaa, 0x1b, length * 2])
        crc = self._checksum(command)
        self.serial_write(command)
        for sound in sounds:
            sound_bytes = bytearray(sound.encode())
            crc += self._checksum(sound_bytes)
            self.serial_write(sound_bytes)
        self.serial_write(crc)

    def end_combination_play(self):
        """
        End combination play.
        """
        command = bytearray([0xaa, 0x1c, 0x00])
        self.send_command(command, 0xc6)
    
    # Methods for querying and setting module state
    def check_play_state(self):
        """
        Check the current play state can be called at any time.
        """
        command = bytearray([0xaa, 0x01, 0x00])
        self.send_command(command, 0xab)
        response = self.get_response(5)
        if response:
            # Extract the play state from the response and return the corresponding PlayState
            state = response[3]
            if state in [self.PlayState.Stopped, self.PlayState.Playing, self.PlayState.Paused]:
                return state
        return self.PlayState.Fail
    
    def set_cycle_mode(self, mode):
        """
        Sets the cycle mode.
        Args:
            mode: eg DYPlayer.PlayMode.Repeat
        """
        command = bytearray([0xaa, 0x18, 0x01, mode])
        self.send_command(command)

    def set_cycle_times(self, cycles):
        """
        Set how many cycles to play when in cycle modes 0, 1 or 4 (repeat modes).
        Args:
            cycles: number of cycles to play.
        """
        command = bytearray([0xaa, 0x19, 0x02, cycles >> 8, cycles & 0xff])
        self.send_command(command)

    def set_eq(self, eq):
        """
        Set the equalizer setting.
        Args:
            eq: e.g. `DYPlayer.Eq.Normal`.
        """
        command = bytearray([0xaa, 0x1a, 0x01, eq])
        self.send_command(command)

    def select(self, number):
        """
        Select a sound file without playing it.
        Args:
            number: e.g. `1` for `00001.mp3`.
        """
        command = bytearray([0xaa, 0x1f, 0x02, number >> 8, number & 0xff])
        self.send_command(command)

    def volume_increase(self):
        """
        Increase the playback volume by 1.
        """
        command = bytearray([0xaa, 0x14, 0x00])
        self.send_command(command, 0xbe)

    def volume_decrease(self):
        """
        Decrease the playback volume by 1.
        """
        command = bytearray([0xaa, 0x15, 0x00])
        self.send_command(command, 0xbf)
    
    def set_volume(self, volume):
        """
        Set the playback volume between 0 and 30.
        Default volume if not set: 20.
        """
        command = bytearray([0xaa, 0x13, 0x01, volume])
        self.send_command(command)

    def get_first_in_dir(self):
        """
        Get number of the first song in the currently selected directory.
        """
        command = bytearray([0xaa, 0x11, 0x00])
        self.send_command(command, 0xbb)
        response = self.get_response(6)
        if response:
            # Extract and return the first sound number in the directory from the response
            return (response[3] << 8) | response[4]
        return 0

    def get_sound_count_dir(self):
        """
        Get the amount of sound files in the currently selected directory.
        Excluding files in sub directories.
        """
        command = bytearray([0xaa, 0x12, 0x00])
        self.send_command(command, 0xbc)
        response = self.get_response(6)
        if response:
            # Extract and return the count of sound files in the current directory from the response
            return (response[3] << 8) | response[4]
        return 0
    
    def get_playing_device(self):
        """
        Get the storage device that is currently used for playing sound files.
        """
        command = bytearray([0xaa, 0x0a, 0x00])
        self.send_command(command, 0xb4)
        response = self.get_response(5)
        if response:
            # Extract the device from the response and return the corresponding Device
            device = response[3]
            if device in [self.Device.Usb, self.Device.Sd, self.Device.Flash]:
                return device
        return self.Device.Fail

    def set_playing_device(self, device):
        """
        Set the device number the module should use.
        Args:
            device: to set e.g DYPlayer.Device.Sd
        """
        command = bytearray([0xaa, 0x0b, 0x01, device])
        self.send_command(command)

    def get_sound_count(self):
        """
        Get the amount of sound files on the current storage device.
        """
        command = bytearray([0xaa, 0x0c, 0x00])
        self.send_command(command, 0xb6)
        response = self.get_response(6)
        if response:
            # Extract and return amount of sound files from the response
            return (response[3] << 8) | response[4]
        return 0

    def get_playing_sound(self):
        """
        Get the currently playing file by number.
        """
        command = bytearray([0xaa, 0x0d, 0x00])
        self.send_command(command, 0xb7)
        response = self.get_response(6)
        if response:
            # Extract and return the sound number from the response
            return (response[3] << 8) | response[4]
        return 0
    
    # Private helper methods
    def _flush(self):
        """
        Flushes the UART buffer to clear any pending data.
        """
        self.uart.read(self.uart.any())
    
    def _validate_crc(self, data):
        """
        Validate data with CRC byte (last byte should be the CRC byte).
        """
        crc = data[-1]
        return self._checksum(data[:-1]) == crc
    
    def _checksum(self, data):
        """
        Calculate the sum of all bytes in a data as a simple "CRC".
        """
        sum = 0
        for byte in data:
            sum += byte
            sum &= 0xFF  # Ensuring sum stays within the range of a byte (0-255)
        return sum
    
    def _by_path_command(self, command, device, path):
        """
        Convert a path to a command with a specific format and send it to the module.
        """ 
        len_path = len(path)
        if len_path < 1:
            return

        # Count '/' in path and determine new length, excluding root slash
        new_len = len_path + path.count('/') - (1 if path.startswith('/') else 0)

        # Construct command bytearray
        byte_command = bytearray([0xaa, command, new_len + 1, device]) + bytearray(path[0].encode())
        j = 5  # Starting index for appending to command

        # Process and append the rest of the path to the command
        for i in range(1, len_path):
            if path[i] == '.' or path[i] == '/':
                byte_command.append(ord('﹡'))
                if path[i] == '/':
                    j += 1
            else:
                byte_command.append(ord(path[i].upper()))
            j += 1

        # Send the command
        self.send_command(byte_command)