from collections import defaultdict
from concurrent import futures
import queue
import grpc
import numpy as np
from backends.bark import BarkBackend
from futuracommon.protos import tts_pb2
from futuracommon.protos import tts_pb2_grpc
from futuracommon.protos import healthcheck_pb2_grpc, healthcheck_pb2
import logging

from backends.xtts import XttsBackend

backend = XttsBackend("backends/speakers/2.ogg")
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SYNTSERVICE')

sessions: dict[str, queue.Queue] = {}

class TextToSpeechServicer(tts_pb2_grpc.TextToSpeechServicer):

    def ProcessText(self, request, context):
        if request.session_id in sessions:
            sessions[request.session_id].put(request.text)
            print(f"Added to queue text: {request.text}")
            return tts_pb2.SessionResponse(session_id=request.session_id)
        
        context.abort(grpc.StatusCode.NOT_FOUND, "Session not found")
        return tts_pb2.SessionResponse(session_id=request.session_id)


    def StreamAudio(self, request, context):
        audio_queue = sessions.get(request.session_id)
        if not audio_queue:
            sessions[request.session_id] = queue.Queue()
            audio_queue = sessions[request.session_id]
        
        print(sessions)
        
        while True:
            text = audio_queue.get()
            print(f"синтез: {text}. ")
            if text:
                data = backend.generate_audio(text)

                audio = data.tobytes()
                print(type(data), type(audio), data[0])
                print(f"отправка {text}")
                yield tts_pb2.AudioChunk(data=audio)

class HealthServicer(healthcheck_pb2_grpc.HealthServiceServicer):
    def Check(self, request, context):
        
        return healthcheck_pb2.HealthResponse(status=1, current_backend=f"{backend.name} ({backend.device}")
 

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tts_pb2_grpc.add_TextToSpeechServicer_to_server(TextToSpeechServicer(), server)
    healthcheck_pb2_grpc.add_HealthServiceServicer_to_server(HealthServicer(), server)
    
    server.add_insecure_port('[::]:50050')
    server.start()
    logger.info("Listening...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()