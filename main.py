from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"This just serves as a commitment message that I will end up finishing the app and it is currently working, with my own fingers" : "."}

if __name__ == "__main__":
    main()
