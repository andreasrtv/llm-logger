from app import socketio, app


if __name__ == "__main__":
    socketio.run(
        app,
        host="::",
        port=5000,
        debug=False,
        log_output=True,
    )
