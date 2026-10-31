"""Optional experimental face matcher. Install requirements separately; CPU inference can be slow."""
import os, base64, tempfile
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from deepface import DeepFace

app = FastAPI()
class Reference(BaseModel):
    studentId: str
    imageBase64: str
class MatchRequest(BaseModel):
    imageBase64: str
    references: list[Reference]

@app.get('/health')
def health(): return {'ok': True}

@app.post('/match')
def match(payload: MatchRequest, x_recognition_key: str = Header(default='')):
    expected=os.getenv('RECOGNITION_KEY','')
    if not expected or x_recognition_key != expected:
        raise HTTPException(status_code=401,detail='Invalid recognition key')
    with tempfile.TemporaryDirectory() as folder:
        probe=os.path.join(folder,'probe.jpg')
        with open(probe,'wb') as f:f.write(base64.b64decode(payload.imageBase64,validate=True))
        best=None
        for i,ref in enumerate(payload.references):
            filename=os.path.join(folder,f'ref{i}.jpg')
            try:
                with open(filename,'wb') as f:f.write(base64.b64decode(ref.imageBase64,validate=True))
                result=DeepFace.verify(img1_path=probe,img2_path=filename,model_name='Facenet512',detector_backend='opencv',enforce_detection=True,align=True)
                if result.get('verified') and (best is None or result['distance'] < best['distance']):
                    best={'studentId':ref.studentId,'distance':float(result['distance'])}
            except Exception as exc:
                print('Could not match reference:',ref.studentId,type(exc).__name__)
        if best:
            return {'studentId':best['studentId'],'confidence':round(max(0,1-best['distance'])*100,2)}
        return {'studentId':None,'confidence':None}
