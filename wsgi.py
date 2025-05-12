from app import app, socketio

if __name__ == "__main__":
    # For production, disable debug mode
    socketio.run(app, debug=False)