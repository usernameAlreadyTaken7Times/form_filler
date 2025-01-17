from fastapi import FastAPI, HTTPException, Query
from gensim.models import KeyedVectors
import jieba
import uvicorn
import os
import asyncio
from threading import Thread

class SynonymAPI:
    def __init__(self, model_path: str):
        self.app = FastAPI()
        self.model = None
        self.model_path = model_path
        self._setup_routes()
        self.model_loaded_callback = None  # Callback to notify when the model is loaded
        self.server = None
        self.server_thread = None
        
        @self.app.on_event("startup")
        async def load_model():
            await self._load_model()

    def set_model_loaded_callback(self, callback):
        """Set a callback function to notify when the model is loaded."""
        self.model_loaded_callback = callback

    async def _load_model(self):
        """Load the model during startup."""
        try:
            print("Loading model, please wait...")
            self.model = KeyedVectors.load(self.model_path)
            if self.model_loaded_callback:
                self.model_loaded_callback(success=True, error=None)  # Notify success
        except Exception as e:
            if self.model_loaded_callback:
                self.model_loaded_callback(success=False, error=str(e))

    def _setup_routes(self):
        """Define the API routes."""
        
        @self.app.get("/synonyms/{word}")
        async def get_synonyms(word: str, top_n: int = Query(4, ge=1, description="Number of synonyms to return")): # 获取同义词，top_n默认为4，即返回前4个同义词
            if not self.model:
                raise HTTPException(status_code=500, detail="The model is not loaded")
            try:
                similar_words = self.model.most_similar(word, topn=top_n)
                return {"word": word, "synonyms": [w for w, _ in similar_words]}
            except KeyError:
                raise HTTPException(status_code=404, detail=f"The word '{word}' was not found in the model. Please check your input.")

        @self.app.get("/tokenize")
        async def tokenize_text(text: str):
            tokens = jieba.lcut(text)
            return {"text": text, "tokens": tokens}
        
        # three funny routes to handle wrong spellings
        @self.app.get("/symonoyms")
        async def null():
            return {"message": "Wrong spelling, please check the URL."}
        
        @self.app.get("/symonyms")
        async def null():
            return {"message": "Wrong spelling, please check the URL."}
        
        @self.app.get("/synonoyms")
        async def null():
            return {"message": "Wrong spelling, please check the URL."}
        
        # test weather the API is running
        @self.app.get("/")
        async def null():
            return {"message": "Synonym API is running!"}

    def run(self, host="127.0.0.1", port=8000, backup_host="127.0.0.1", backup_port=8001):
        """Run the FastAPI app with a backup host and port."""
        def run_server(host, port):
            config = uvicorn.Config(self.app, host=host, port=port, reload=False)
            server = uvicorn.Server(config)
            return server

        try:
            self.server = run_server(host, port)
            self.server_thread = Thread(target=self.server.run)
            self.server_thread.start()
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Port {port} is in use, switching to backup port {backup_port}")
                self.server = run_server(backup_host, backup_port)
                self.server_thread = Thread(target=self.server.run)
                self.server_thread.start()
            else:
                raise e

    def stop(self):
        """Stop the FastAPI app and unload the model to release memory."""
        if self.server:
            self.server.should_exit = True
            self.server_thread.join()
        self.model = None
    
    def get_host(self): # 获取主机地址
        return self.server.config.host

    def get_port(self): # 获取端口号
        return self.server.config.port

# Example of using the class

# model_path = os.getenv("MODEL_PATH", r"C:\\Users\\86781\\VS_Code_Project\\FormFiller\\asset\\models\\cc.zh.300.bin")
# model_path = os.getenv("MODEL_PATH", r"C:\\Users\\86781\\VS_Code_Project\\FormFiller\\asset\\models\\sgns.merge.word.bin")
model_path = os.getenv("MODEL_PATH", r"C:\\Users\\86781\\VS_Code_Project\\FormFiller\\asset\\models\\merge_sgns_bigram_char300.txt.bin")
api = SynonymAPI(model_path=model_path)

def notify_model_loaded(success: bool, error: str):
    if success:
        print("Model loaded successfully!")
    else:
        print(f"Failed to load model: {error}")

api.set_model_loaded_callback(notify_model_loaded)
print("Starting the API server...")
api.run()


