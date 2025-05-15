import onnxruntime as ort
import os

class ModelConfig:
    CLASS_COLORS = {"Pothole": [19, 19, 220]}  # crimson in BGR
    INPUT_SIZE = (640, 640)
    MODEL_PATH = os.getenv("MODEL_PATH", "../model/model.onnx")

def load_model(model_path: str) -> ort.InferenceSession:
    try:
        ort_session = ort.InferenceSession(model_path)
        
        print('-'*40 , '\n\t Loading the ONNX model \n' , '-'*40)

        ort_session_input_name = ort_session.get_inputs()[0].name
        ort_session_output_name = ort_session.get_outputs()[0].name

        print('ort_input_name' , ort_session_input_name)
        print("ort_output_name" , ort_session_output_name)
        
        return ort_session
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {str(e)}")
    
