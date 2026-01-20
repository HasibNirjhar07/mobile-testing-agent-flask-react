from loguru import logger

def init_sockets(socketio):
    @socketio.on('connect')
    def handle_connect():
        logger.info("Client connected to socket")

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info("Client disconnected from socket")
