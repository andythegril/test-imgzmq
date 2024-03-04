import threading
import cv2
import imagezmq
import time


def stream_video(url, camera_name):
    sender = imagezmq.ImageSender(connect_to="tcp://127.0.0.1:5555")
    cap = cv2.VideoCapture(url)
    while cap.isOpened():
        ret, frame = cap.read()
        print(f'Sending frame from {camera_name} using ImgZMQ')
        if not ret:
            print(f"Failed to grab frame for {camera_name}")
            break
        sender.send_image(camera_name, frame)
        time.sleep(0.1)
    cap.release()


def get_camera_urls():
    with open('sources.streams', 'r') as file:
        videoDoc = file.read().splitlines()
        # return file.read().splitlines()
        for video in videoDoc:
            print('sources: ', video)
        return videoDoc


def send_video_streams():
    urls = get_camera_urls()
    threads = []
    for camera_index, url in enumerate(urls, start=1):
        camera_name = f"camera{camera_index}"
        thread = threading.Thread(target=stream_video, args=(url, camera_name))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    send_video_streams()
