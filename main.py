from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File
from policy.fileIngestion import  parse_markdown, parse_headers
import os

app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"This just serves as a commitment message that I will end up finishing the app and it is currently working, with my own fingers" : "."}

@app.get("/upload-policy")
async def policyHandling(file: UploadFile = File(...)):
    tempFilePath = f"temp_{file.filename}"
    try:
        with open(tempFilePath, "wb") as buffer: 
            buffer.write(await file.read())
        markDownData = await parse_markdown(tempFilePath)
        chunks = await parse_headers(tempFilePath)
        responseData = []
        for chunk in chunks:
            responseData.append(
                {
                    "metadata" : chunk.metadata,
                    "text": chunk.page_content[:200]
                }
            )
        return {
            "status": "success",
            "filename": file.filename,
            "total_chunks": len(chunks),
            "data": responseData
        }
    except Exception as e:
        return {"status" : "error", "message": str(e)}
    finally:
        if os.path.exists(tempFilePath):
            os.remove(tempFilePath)   
        

if __name__ == "__main__":
    main()
