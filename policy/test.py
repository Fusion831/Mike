import asyncio
from policy.fileIngestion import parse_markdown, parse_headers

async def main():
    tempFilePath = r"/home/daksh/dev/Projects/BetterCallLaw/documents/CSNE24HP0125481_002.pdf"
    data = await parse_markdown(tempFilePath)
    with open("TESTING.md", "w") as file:
        file.write(data)
    chunks = await parse_headers(data)
    for chunk in chunks:
        print(chunk.metadata)
asyncio.run(main())
