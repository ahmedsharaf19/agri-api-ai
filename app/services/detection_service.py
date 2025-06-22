import io, cv2, numpy as np, base64
from PIL import Image
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet import preprocess_input
from app.services.groq_doctor import get_treatment_text
import os


model_path = os.path.join(os.path.dirname(__file__), "..", "models", "yolo.pt")
model = YOLO(model_path)
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "class.h5")
mobilenet_model = load_model(model_path)

custom_class_names = {0: 'Early Blight', 1: 'Healthy', 2: 'Late Blight', 3: 'Leaf Miner', 4: 'Leaf Mold', 5: 'Mosaic Virus', 6: 'Septoria', 7: 'Spider Mites', 8: 'Yellow Leaf Curl Virus'}

async def process_image(file):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model(image)

    boxes = results[0].boxes.xyxy.cpu().numpy()
    class_ids = results[0].boxes.cls.cpu().numpy()

    detected_diseases = set()

    for box, class_id in zip(boxes, class_ids):
        x1, y1, x2, y2 = map(int, box)
        crop = image[y1:y2, x1:x2]
        resized = cv2.resize(crop, (224, 224))
        preprocessed = preprocess_input(resized)
        preprocessed = np.expand_dims(preprocessed, axis=0)
        preds = mobilenet_model.predict(preprocessed)
        pred_idx = np.argmax(preds, axis=-1)[0]
        disease = custom_class_names[pred_idx]
        detected_diseases.add(disease)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(image, disease, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    pil_img = Image.fromarray(image)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    img_url = f"data:image/png;base64,{img_base64}"
    
    # تحويل الأمراض المكتشفة إلى نص
    if detected_diseases:
        diseases_list = list(detected_diseases)
        diseases_str = ", ".join(diseases_list)
        treatment = await get_treatment_text(diseases_str)
    else:
        diseases_list = []
        treatment = "لا يوجد أمراض مكتشفة في الصورة. النبات يبدو صحياً."

    return {
        "image_url": img_url,
        "diseases": diseases_list,
        "treatment": treatment
    }
