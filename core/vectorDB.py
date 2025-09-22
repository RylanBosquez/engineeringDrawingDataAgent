import json
import chromadb
import requests
import re
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings


class OllamaEmbedder(EmbeddingFunction):
    def __init__(self, model="nomic-embed-text", url="http://localhost:11434/api/embeddings"):
        self.model = model
        self.url = url

    def __call__(self, texts: Documents) -> Embeddings:
        embeddings = []
        for text in texts:
            response = requests.post(self.url, json={"model": self.model, "prompt": text})
            response.raise_for_status()
            data = response.json()
            embeddings.append(data["embedding"])
        return embeddings

    def name(self) -> str:
        return f"ollama-{self.model}"


def formatDrawingRecord(record: dict) -> str:
    parts = []
    for key, value in record.items():
        if key == "Revision History" and isinstance(value, dict):
            valueStr = "\n" + "\n".join(
                [f'  - "{rev}": {json.dumps(details, ensure_ascii=False)}' for rev, details in value.items()]
            ) if value else "None"
        elif key == "Part Numbers" and isinstance(value, dict):
            valueStr = "\n" + "\n".join(
                [f'  - "{pn}": Qty: {details.get("Qty", "")}, Description: {details.get("Description", "")}'
                 for pn, details in value.items()]
            ) if value else "None"
        elif key == "Notes":
            if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                stripped = value[1:-1].strip()
                splitNotes = [note.strip().strip("'").strip('"') for note in stripped.split("', '")]
                valueStr = "\n" + "\n".join([f'  - {note}' for note in splitNotes])
            else:
                valueStr = f"  - {value}" if value else "None"
        elif isinstance(value, list):
            valueStr = "\n  - " + "\n  - ".join(value) if value else "None"
        elif isinstance(value, dict):
            valueStr = json.dumps(value, ensure_ascii=False) if value else "None"
        else:
            valueStr = str(value) if value else "None"
        parts.append(f"*** {key} ***: {valueStr}")
    return "\n".join(parts)


def loadDrawingCollection(jsonPath: str = "./assets/engineeringDrawing.json", dbPath: str = "./drawingDB"):
    client = chromadb.PersistentClient(path=dbPath)
    collection = client.get_or_create_collection(
        name="engineeringDrawings",
        embedding_function=OllamaEmbedder()
    )

    with open(jsonPath, "r", encoding="utf-8") as file:
        drawingData = json.load(file)

    documents = []
    ids = []
    metadatas = []

    for i, record in enumerate(drawingData):
        if isinstance(record, dict):
            formattedText = formatDrawingRecord(record)
            documents.append(formattedText)
            ids.append(f"doc_{i}")
            metadatas.append({"drawingNumber": record.get("Drawing Number", "")})

    if documents:
        collection.add(documents=documents, ids=ids, metadatas=metadatas)

    return collection


def queryDrawings(collection, queryText: str, nResults: int = 5):
    matchFull = re.search(r"R\d{7}", queryText.upper())
    matchPartial = re.search(r"\b\d{7}\b", queryText)

    if matchFull:
        drawingNumber = matchFull.group(0)
        queryResults = collection.query(
            query_texts=[queryText],
            n_results=1,
            where={"drawingNumber": drawingNumber}
        )
    elif matchPartial:
        drawingNumber = "R" + matchPartial.group(0)
        queryResults = collection.query(
            query_texts=[queryText],
            n_results=1,
            where={"drawingNumber": drawingNumber}
        )
    else:
        queryResults = collection.query(
            query_texts=[queryText],
            n_results=nResults
        )

    return queryResults["documents"][0]
