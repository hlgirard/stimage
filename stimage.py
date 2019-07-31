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
CAPILLARY_LENGTH = 14400 # for 100mm capillary
CAPILLARY_X_INTERVAL = 1800
CAPILLARY_Y_INTERVAL = 3000

def initialize_stage():
    '''Initialize stage'''
    stage = Stage()

    click.pause(info='Make sure stage is ready to initialize. Press any key to start...')
    stage.initialize_stage()

    return stage

def check_alignment(stage):
    '''Moves the stage to check that the capillary holder is correcly aligned and the focus is satisfactory'''
    stage.moveX(-15000)
    click.pause(info='Check alignment and focus. Press any key to move down.')
    stage.moveY(CAPILLARY_Y_INTERVAL)
    click.pause(info='Check alignment and focus. Press any key to move left.')
    stage.moveX(15000)
    click.pause(info='Check alignment and focus. Press any key to move back to start position')
    stage.moveY(-1 * CAPILLARY_Y_INTERVAL)
    return


def main(duration, directory, stage=None, bCheckAlignment=False, n_tubes=1):

    # Initialize stage
    if not stage:
        stage = initialize_stage()

    # Check alignment if requested
    if bCheckAlignment:
        click.pause(info='ALIGNEMENT - Align stage to the back left corner and press any key to continue...')
        check_alignment(stage)

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

    with tqdm(desc='Time', position=0, leave=True, total=int(t_end-t_int), disable=(duration == -1)) as bar_time:
        while (time() < t_end) or (duration == -1):
            with tqdm(total=n_tubes*n_img_per_tube, desc="Run #{}".format(seq_nb), position=1, leave=False) as bar_run:
                for i in range(n_tubes):
                    for j in range(n_img_per_tube):

                        # Wait for previous camera download to finish, if any
                        if async_work:
                            async_work.wait()

                        # Capture and save a new image
                        filename = os.path.join(directory, datetime.datetime.now().strftime("%y%m%d_%H%M%S") + '_x{}_y{}_seq{}_CrystKinetics.jpg'.format(j, i, seq_nb))
                        async_work = pool.apply_async(camera_full, (filename,))

                        # Wait until capture is done
                        sleep(1.1) # FIXME: Correct time offset if necessary.

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
@click.option('-n', '--tubes', default=1, help='Number of tubes to image. Default 1')
@click.option('-t', '--tot-time', default=1, help='Total duration of experiment in hours. -1 for unlimitted.')
@click.argument('directory', type=click.Path(), required=True)
def cli(directory, verbose, check, tubes, tot_time):

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

    main(bCheckAlignment=check, n_tubes=tubes, directory=directory, duration=tot_time)


if __name__ == '__main__':
    cli()