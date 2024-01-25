# dyplayer-micropython
UART Control of DY-XXXX mp3 modules using MicroPython

This is a port of [SnijderC's arduino code](https://github.com/SnijderC/dyplayer/) in MicroPython

I have only personally tested the DY-SV17F and DY-SV19R, but since SnijderC's code works on the below I'd assume the same

| Model Name | Capacity | SD Card Support    | Amplifier          | Voltage | Tested |
|------------|----------|--------------------|--------------------|---------|--------|
| DY-SV17F   | 4MB      | No                 | 3-5W (4Ω/8Ω)       | 5VDC    | Yes    |
| DY-SV19R   | 4MB      | No                 | 3-5W (4Ω/8Ω)       | 5VDC    | Yes    |
| DY-SV19T   | NA       | Yes, Max. 32GB     | 3-5W (4Ω/8Ω)       | 5VDC    | No     |
| DY-SV8F    | 8MB      | No                 | 3-5W (4Ω/8Ω)       | 5VDC    | No     |
| DY-HV20T   | NA       | Yes, Max. 32GB     | 3-5W (4Ω/8Ω)       | 5VDC    | No     |
| DY-HV8F    | 8MB      | No                 | 10W (8Ω)/20W (4Ω)  | 6-35VDC | No     |
| DY-HV20T   | NA       | Yes, Max. 32GB     | 10W (8Ω)/20W (4Ω)  | 6-35VDC | No     |
| DY-SV5W    | NA       | Yes, Max. 32GB     | 3-5W (4Ω/8Ω)       | 5VDC    | Yes    |
