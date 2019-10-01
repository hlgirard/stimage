# stimage

Python program to image different parts of a setup using an XY stage controlled by stepper motors.
This command line script enables the control of a two-axis linear stage and a DSLR to take images of rectilinear samples (e.g. tubes) arranged in a grid at regular intervals.

The `stage` object uses the Adafruit libraries to control the steppers connected to an Adafruit DC & Stepper Motor HAT mounted on a Raspberry Pi.

The `camera` object is a wrapper for the OpenCV DSLR interfacing enabled by `cv2.VideoCapture`.

## Installation

Clone the stimage repository

```
git clone https://github.com/hlgirard/stimage.git
cd stimage
```

Install with pip as editable

```
pip install -e .
```

### Adjust the code to your setup

At a minimum, the following constants present in the code should be checked and modified prior to using this script:

In `stimage.py`
- `CAPILLARY_LENGTH`: total length in interleaved steps to be imaged
- `CAPILLARY_X_INTERVAL`: interval between successive images along the X-axis
- `CAPILLARY_Y_INTERVAL`: interval between successive images along the Y-axis

In `control/stage.py`
- `stage.maxX` (and `Y`) [int]: length of the X-axis (respectively, Y-axis) in interleaved steps
- `stage.stepperX` (and `Y`): should be set to `stage.kit.stepper1` or `2` depending on the desired reference frame
- `stage.limXMaxBut` (and `Y`): should be adjusted to reflect the pin number of the lower/upper limit button `Button(<GPIO_PIN_OF_BUTTON>, bounce_time=0.05)`


## Usage

### Quickstart

Use the following command to start imaging 2 tubes for a total of 4 hours with a delay of 1.6 seconds between the capture command and movement of the stage. Checks the alignment of the stage before running by going to the corners of the tubes. Saves all the images to image_directory.

```
stimage --check --tubes 2 --tot-time 4 --delay 1.6 image_directory
```

### Arguments

- `-v`, `--verbose` increase the verbosity level. `-vv` for debug level logging.
- `-c`, `--check` check alignment by going to the corners of the tubes before starting capture.
- `-n`, `--tubes` Number of tubes in the Y direction. Default 1.
- `t`, `--tot-time` Total time of imaging in hours. Default 1.
- `d`, `--delay` Delay between the initiation of the capture command and the next stage movement in seconds to account for camera focusing and exposure. Mandatory.

## Repository structure

- `stimage.py`: main entry point, handles the logic take pictures at a prescribed interval
- `control`
    - `stage.py`: handles the XY stage hardware control logic wrapped in the `Stage` object.
    - `camera.py`: handles the camera hardware control logic.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

