import argparse
import socket

import cv2
import numpy as np


def main():
    parser = argparse.ArgumentParser("receive video data over UDP")

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

    args = parser.parse_args()

    receive_video(args.ip, args.port)


def receive_video(ip: str, port: int):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    print(f"Listening for video frames on {ip}:{port}...")

    # Buffer size for each UDP packet
    buffer_size = 65535  # Maximum UDP packet size

    data = b""  # Buffer to hold fragmented frames
    while True:
        try:
            # Receive packet
            packet, _ = sock.recvfrom(buffer_size)
            if not packet:
                continue

            # Check for end-of-frame marker (customize if needed)
            if packet.endswith(b"END"):
                data += packet[:-3]  # Exclude the marker

                # Convert received bytes into a NumPy array
                frame_data = np.frombuffer(data, dtype=np.uint8)

                # Decode the frame using OpenCV
                frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Display the frame
                    cv2.imshow("Live Video", frame)

                    # Quit with 'q'
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                # Clear buffer for next frame
                data = b""
            else:
                # Accumulate packet data
                data += packet

        except Exception as e:
            print(f"Error: {e}")
            data = b""

        except KeyboardInterrupt:
            print("\nExiting.")
            break

    # Cleanup
    sock.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
