from pydantic import BaseModel

class IncomingMessage(BaseModel):
    sender: str
    channel: str  
    message: str