from datetime import datetime
import time
import cv2
import numpy as np
import imagezmq
import threading
import os
import logging

from flask import Flask, render_template, Response, jsonify, url_for, session
from flask_cors import CORS
from flask import abort

from threading import Lock

# Config logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'bechimcut'
app.config['UPLOAD_FOLDER'] = 'static/files'

# global
frame_dict = {}
frame_dict_lock = Lock()


def frame_receiver():
    global frame_dict
    try:
        receiver = imagezmq.ImageHub(open_port='tcp://*:5555')
        logging.debug('ImageZMQ receiver started')
        while True:
            camera_name, frame = receiver.recv_image()
            with frame_dict_lock:
                frame_dict[camera_name] = frame
            logging.debug(f'ImgZMQ receiving frames from {camera_name} at {datetime.now()}, '
                          f'Type of frame data: {type(frame)}')
    except Exception as e:
        logging.error("General error processing video: %s", e, exc_info=True)
        time.sleep(5)


@app.route('/video_feed/<camera_name>')
def video_feed(camera_name):
    placeholder_data = open('static/files/static_img.webp', 'rb').read()

    def generate():
        while True:
            with frame_dict_lock:
                frame = frame_dict.get(camera_name, None)
            if frame is not None:
                if isinstance(frame, np.ndarray):
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if not ret:
                        logging.error("Error encoding frame")
                        continue
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    logging.error("Frame is not a NumPy array. Check the received frame format.")
                    time.sleep(1)
            else:
                logging.debug(f"No frame available for {camera_name}.")
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + placeholder_data + b'\r\n')
                time.sleep(1)
                continue

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/camera_urls')
def camera_urls():
    # with frame_dict_lock:
    #     logging.debug("Complete frame_dict contents: %s", frame_dict)
    #     camera_names = list(frame_dict.keys())
    camera_names = ["camera1", "camera2",                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             "camera3", "camera4"]
    return jsonify(camera_names)


@app.route('/all-cameras', methods=['GET', 'POST'])
def see_all_cams():
    try:
        session.clear()
        return render_template('showallcams.html')
    except Exception as e:
        logging.error(e)
        abort(5000)


if __name__ == "__main__":
    frame_receiver_thread = threading.Thread(target=frame_receiver, daemon=True)
    frame_receiver_thread.start()
    app.run(debug=True, threaded=True, use_reloader=False)


