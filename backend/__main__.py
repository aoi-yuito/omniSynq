from backend import ApiServer, BASE_DIR

# Create an instance of your custom class at the module level
server = ApiServer(BASE_DIR)

def main():
    # To run in development with auto-reload:
    # Note: the uvicorn.run call inside the `run` method handles the execution
    server.run(reload=False)

    # To run in production without reload:
    # server.run(reload=False)

if __name__ == "__main__":
    main()