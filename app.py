from importlib import import_module
import os
import flask
from markupsafe import escape
import Pi
from multiprocessing import Process

#import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_pi import Camera


app = flask.Flask(__name__)
DOWNLOAD_FOLDER = './projects'
BASE_DIR = './'

@app.route('/')
def index():
    return flask.render_template('cam.html')

@app.route('/cam/')
@app.route('/cam/<status>', methods=['GET','POST'])
def cam(status=None):
    return flask.render_template('cam.html', status=status, ip=flask.request.host)

@app.route('/record/<fileName>', methods=['GET','POST'])
def start(fileName=None):
    Pi.record(fileName)
    return flask.render_template('cam.html', ip=flask.request.host, status='record')

@app.route('/delete/<fileName>', methods=['GET','POST'])
def remove(fileName=None):
    Pi.delete(fileName)
    return flask.render_template('cam.html', ip=flask.request.host, status='list')

@app.route('/stop', methods=['GET','POST'])
def stop():
    Pi.stop()
    return flask.render_template('cam.html', ip=flask.request.host, status='stop')

@app.route('/update', methods=['GET','POST'])
def update():
    Pi.update()
    return redirect("http://" + flask.request.host + "/cam")

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return flask.send_from_directory(DOWNLOAD_FOLDER, filename=filename, as_attachment=True)

def gen(camera):
    """video streaming generator function"""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/<path:req_path>')
def dir_listing(req_path):
    # Show directory contents
    abs_path = os.path.join(BASE_DIR, req_path)
    files = os.listdir(abs_path)
    return flask.render_template('cam.html', files=files, ip=flask.request.host, status='list')

@app.route('/preview')
def video_feed():
    """video streaming route put this in the src attribute of an img tag"""
    return flask.Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=5000, debug=False)
