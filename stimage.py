'''
Image capillary tubes repeatedly using a DLSR camera and XY stage mounted on a microscope.
'''

import datetime
from multiprocessing import Pool
import os
import logging
from time import time, sleep

import click
from tqdm import tqdm

from control.stage import Stage
from control.camera import camera_full

# Constants
## Capillary tube length and interval between pictures
CAPILLARY_LENGTH = 4000 # for 100mm capillary
CAPILLARY_X_INTERVAL = 250
CAPILLARY_Y_INTERVAL = 250

## Delay between command to image and end of image capture (before stage can move)
D300_DELAY = 0.5 # seconds
D750_DELAY = 0.2 # seconds

def initialize_stage(x_only=False):
    '''Initialize stage'''
    stage = Stage()

    click.pause(info='Make sure stage is ready to initialize. Press any key to start...')
    stage.initialize_stage(x_only=x_only)

    return stage

def check_alignment(stage, x_only=False):
    '''Moves the stage to check that the capillary holder is correcly aligned and the focus is satisfactory'''
    stage.moveX(-4000)
    if not x_only:
        click.pause(info='Check alignment and focus. Press any key to move down.')
        stage.moveY(CAPILLARY_Y_INTERVAL)
    click.pause(info='Check alignment and focus. Press any key to move left.')
    stage.moveX(4000)
    if not x_only:
        click.pause(info='Check alignment and focus. Press any key to move back to start position')
        stage.moveY(-1 * CAPILLARY_Y_INTERVAL)


def main(duration, directory, delay, stage=None, bCheckAlignment=False, n_tubes=1):

    # Initialize stage
    if not stage:
        stage = initialize_stage(x_only=(n_tubes == 1))

    # Check alignment if requested
    if bCheckAlignment:
        click.pause(info='ALIGNMENT - Align stage to the back left corner and press any key to continue...')
        check_alignment(stage, x_only=(n_tubes == 1))

    # Start imaging loop
    x0 = stage.posX
    y0 = stage.posY

    n_img_per_tube = CAPILLARY_LENGTH // CAPILLARY_X_INTERVAL

    click.pause("READY - Press any key to start...")

    t_end = int(time() + duration * 3600) # t_end in unix seconds
    t_int = int(time())
    seq_nb = 0 # Sequence number

    # Create a pool of 1 worker
    pool = Pool(processes=1)
    async_work = None

    with tqdm(desc='Time', position=0, leave=True, total=int(t_end-t_int), disable=(duration == -1 or logging.getLogger().getEffectiveLevel() == logging.DEBUG)) as bar_time:
        while (time() < t_end) or (duration == -1):
            with tqdm(total=n_tubes*n_img_per_tube, desc="Run #{}".format(seq_nb), position=1, leave=False, disable=logging.getLogger().getEffectiveLevel() == logging.DEBUG) as bar_run:
                for i in range(n_tubes):
                    for j in range(n_img_per_tube):

                        # Wait for previous camera download to finish, if any
                        if async_work:
                            logging.debug('main - Waiting for camera transfer to finish...')
                            async_work.get(timeout=10)

                        # Capture and save a new image
                        filename = os.path.join(directory, datetime.datetime.now().strftime("%y%m%d_%H%M%S") + '_x{}_y{}_seq{}_CrystKinetics.jpg'.format(j, i, seq_nb))
                        logging.debug('main - Starting camera worker')
                        async_work = pool.apply_async(camera_full, (filename,))

                        # Wait until capture is done
                        sleep(delay)
                        # Goto next imaging position
                        direction = -1 if i % 2 == 0 else 1
                        stage.moveX(direction * CAPILLARY_X_INTERVAL)

                        # Update progress bars
                        bar_run.update(1)
                        t_now = int(time())
                        bar_time.update(t_now-t_int)
                        t_int = t_now

                    if i < n_tubes-1:
                        stage.moveY(CAPILLARY_Y_INTERVAL)
        
            stage.goto(x0, y0)
            seq_nb += 1

    logging.info("Capture done.")


@click.command()
@click.version_option()
@click.option('-v', '--verbose', count=True, help='Increase verbosity')
@click.option('-c', '--check', is_flag=True, help='Check alignment of the stage before starting')
@click.option('-n', '--tubes', default=1, help='Number of tubes to image. Default 1.')
@click.option('-t', '--tot-time', default=1, help='Total duration of experiment in hours. -1 for unlimitted. Default 1.')
@click.option('-d', '--delay', default=0.2, help='Delay necessary to take the picture. 300 for D300, 750 for D750, or value in seconds. Default 750.')
@click.argument('directory', type=click.Path(), required=True)
def cli(directory, verbose, check, tubes, tot_time, delay):

    # Setup logging
    if verbose == 0:
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

    # Make directory if it does not exist
    if not os.path.isdir(directory):
        os.mkdir(directory)

    # Extract delay
    if delay == '300':
        time_delay = D300_DELAY
    elif delay == '750':
        time_delay = D750_DELAY
    else:
        time_delay = float(delay)

    main(bCheckAlignment=check, n_tubes=tubes, directory=directory, duration=tot_time, delay=time_delay)


if __name__ == '__main__':
    cli()