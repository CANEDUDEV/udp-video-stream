import argparse
import socket

from linuxpy.video.device import Device, VideoCapture


def main():
    parser = argparse.ArgumentParser(description="stream video data over UDP")

    parser.add_argument(
        "--ip",
        default="127.0.0.1",
        help="IP address of the receiver (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default="5000",
        help="port number of the receiver (default: 5000)",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default="0",
        help="camera ID, e.g. 0 for /dev/video0 (default: 0)",
    )

    args = parser.parse_args()

    stream_video(args.ip, args.port, args.camera)


def stream_video(ip: str, port: int, camera_index: int = 0):
    camera = Device.from_id(camera_index)
    camera.open()

    video = VideoCapture(camera)
    video.set_format(1280, 720, "MJPG")
    video.open()

    # Set up the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_address = (ip, port)
    print(f"Streaming video to {ip}:{port}...")

    try:
        for frame in video:
            # Transmit the frame in chunks if needed
            max_packet_size = 65507  # Max size for UDP
            for i in range(0, len(frame), max_packet_size):
                chunk = frame[i : i + max_packet_size]
                sock.sendto(chunk, receiver_address)

            # Send an end-of-frame marker
            sock.sendto(b"END", receiver_address)

    except KeyboardInterrupt:
        print("\nStreaming stopped.")

    finally:
        # Cleanup
        sock.close()
        video.close()
        camera.close()


if __name__ == "__main__":
    main()
