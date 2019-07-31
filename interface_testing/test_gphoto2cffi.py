import gphoto2cffi as gp

# List all attached cameras that are supported
cams = gp.list_cameras()

# Get a camera instance by specifying a USB bus and device number
my_cam = gp.Camera(bus=4, device=1)

# Get an instance for the first supported camera
my_cam = gp.Camera()
# or
my_cam = next(gp.list_cameras())

# Capture an image to the camera's RAM and get its data
imgdata = my_cam.capture()

# Grab a preview from the camera
previewdata = my_cam.get_preview()

# Get a list of files on the camera
files = tuple(my_cam.list_all_files())

# Iterate over a file's content
with open("image.jpg", "wb") as fp:
    for chunk in my_cam.files[0].iter_data():
        fp.write(chunk)

# Get a configuration value
image_quality = my_cam.config['capturesettings']['imagequality'].value
# Set a configuration value
my_cam.config['capturesettings']['imagequality'].set("JPEG Fine")