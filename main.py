from server.server import Server
import sys

if __name__ == "__main__":
    myServer = Server(video_name=sys.argv[1])
    myServer.run()
