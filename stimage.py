import click
import datetime
import logging
from time import sleep, time

from control.stage import Stage
from control.camera import Camera

# Constants
CAPILLARY_LENGTH = 20000 # FIXME: length of capillary in stepper steps
CAPILLARY_X_INTERVAL = 1000 # FIXME: distance between pictures along the X-axis
CAPILLARY_Y_INTERVAL = 1500 # FIXME: Interval along Y-direction between two capillaries

def initialize_stage():
    '''Initialize stage'''
    stage = Stage()

    click.pause(info='Make sure stage is ready to initialize. Press any key to start...')
    stage.initialize_stage()

    return stage

def initialize_camera():
    '''Initialize camera connection'''

    return Camera()

def check_alignment(stage):
    '''Moves the stage to check that the capillary holder is correcly aligned and the focus is satisfactory'''
    stage.moveX(15000)
    click.pause(info='Check alignment and focus. Press any key to move down.')
    stage.moveY(-1 * CAPILLARY_Y_INTERVAL)
    click.pause(info='Check alignment and focus. Press any key to move left.')
    stage.moveX(-15000)
    click.pause(info='Check alignment and focus. Press any key to move back to start position')
    stage.moveY(CAPILLARY_Y_INTERVAL)
    return


def main(stage=None, camera=None, bCheckAlignment=False, n_tubes=1, duration):

    # Initialize stage
    if not stage:
        stage = initialize_stage()

    # Initialize camera
    if not camera:
        camera = initialize_camera()

    # Wait for user to align the start position
    click.pause(info='READY - Align stage to the back left corner and press any key to continue...')

    # Check alignment if requested
    if bCheckAlignment:
        check_alignement(stage)
    
    # Start imaging loop
    x0 = stage.posX
    y0 = stage.posY

    n_img_per_tube = CAPILLARY_LENGTH // CAPILLARY_X_INTERVAL

    t_end = time() + duration * 3600 # t_end in unix seconds
    seq_nb = 1 # Sequence number

    while (time() < t_end) or (duration == -1):
        with click.progressbar(length=i*j, label="#{}".format(seq_nb)) as bar:
            for i in range(n_tubes):
                for j in range(n_img_per_tube):

                    # Goto imaging position
                    direction = 1 if i % 2 == 0 else -1
                    stage.moveX(direction * CAPILLARY_X_INTERVAL)

                    # Capture an image and save it
                    # TODO: Add experiment name option?
                    filename = datetime.datetime.now().strftime("%y%m%d_%H%M") + 
                            '_x{}_y{}_seq{}_CrystKinetics.jpg'.format(j, i, seq_nb)
                    camera.capture(filename)
                    bar.update(1)

                stage.moveY(-1 * CAPILLARY_Y_INTERVAL)
        
        stage.goto(x0,y0)
        seq_nb += 1

    logging.info("Capture done.")


@click.command()
@click.version_option(version=0.1, prog_name=stimage, )
@click.option('-v', '--verbose', count=True, help='Increse verbosity')
@click.option('-c', '--check-alignment', is_flag=True, help='Check alignment of the stage before starting')
@click.option('-n', '--tubes', default=1, help='Number of tubes to image')
@click.option('-t', '--time', default=1, help='Total duration of experiment in hours. -1 for unlimitted.')
@click.argument('directory', type=click.Path(exists=True), required=True, help='Directory to save images to')
def cli(verbose):

    # Setup logging
    if verbose == 0:
        logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    elif verbose > 1:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

    main(bCheckAlignment=check_alignment, n_tubes=tubes, directory=directory, duration=time)


if __name__ == '__main__':
    cli()