from django.shortcuts import render

# Create your views here.
def base(request):
    return render(request, 'base.html')

def test(request):
    return render(request, 'test.html')


def add_food(request):

    return render(request, 'add_food.html')


from django.shortcuts import render
from django.http import HttpResponse

# def voice_input_form(request):
#     if request.method == "POST":
#         # Get the form data from POST request
#         food_name = request.POST.get("food_name")
#         expiry_date = request.POST.get("expiry_date")

#         # Process form data if necessary (e.g., save to database)
#         return HttpResponse(f"Received food: {food_name}, expiry date: {expiry_date}")
    
#     return render(request, "user/voice_input_form.html")

# views.py
# views.py

# Gemini API Key and Model Configuration
import os
from django.shortcuts import render
from django.conf import settings
from PIL import Image
import google.generativeai as genai
from django.core.files.storage import FileSystemStorage
import logging
from django.http import JsonResponse
from .models import FoodItem

logger = logging.getLogger(__name__)
from dotenv import load_dotenv

# Access the environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')# Fetch the GEMINI_API_KEY from environment variables
API_KEY = os.getenv("GOOGLE_API_KEY")
print(API_KEY)

genai.configure(api_key=API_KEY)
from django.shortcuts import render
from django.http import JsonResponse
from .models import FoodItem
from django.core.files.storage import FileSystemStorage
from PIL import Image
from datetime import datetime, date, timedelta
import logging
import google.generativeai as genai


logger = logging.getLogger(__name__)

def upload_image_and_voice_input(request):
    image_url = None
    expiry_date = None
    image_processed = False

    if request.method == 'POST':
        food_name = request.POST.get('food_name', '')
        expiry_date = request.POST.get('expiry_date', '')
        
        # Check if both food_name and expiry_date are filled
        if food_name and expiry_date:
            # Save data to the database if the fields are filled
            food_item = FoodItem(name=food_name, expiry_date=expiry_date)
            food_item.save()

        # Handle image upload
        if 'image' in request.FILES:
            uploaded_image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_image.name, uploaded_image)
            image_url = fs.url(filename)

            # Store the image filename to be processed later
            request.session['uploaded_image'] = filename

            try:
                # Open the image using PIL
                img = Image.open(uploaded_image)

                # Prepare the model to generate content
                model = genai.GenerativeModel('gemini-1.5-flash')
                caption_response = model.generate_content(
                    ["Extract the expiry date from this image. Only return the date, e.g., '12th Jan 2024'", img]
                )

                # Get the expiry date text from the model response
                extracted_expiry_date = caption_response.text.strip()
                image_processed = True
                expiry_date = extracted_expiry_date
                print(expiry_date)
                # # Convert the extracted expiry date to a proper date format if needed
                # try:
                #     # Assuming expiry_date is in the format '12 Jan 2024'
                #     expiry_date = datetime.strptime(extracted_expiry_date, '%d %b %Y').date()
                # except ValueError:
                #     expiry_date = "Error parsing expiry date"
                #     logger.error(f"Error parsing the expiry date: {extracted_expiry_date}")

                # If both fields are filled and the image is processed, save to the database
                if food_name and expiry_date and expiry_date != "Error parsing expiry date":
                    food_item = FoodItem(name=food_name, expiry_date=expiry_date, image=uploaded_image)
                    food_item.save()

 
                

            except Exception as e:
                logger.error(f"Error while processing the image: {e}")
                expiry_date = "Error generating expiry date"
                image_processed = True

            # Return the expiry date as a JSON response
            return JsonResponse({'expiry_date': str(expiry_date)})

    return render(request, 'user/voice_input_form.html', {
        'expiry_date': expiry_date,
        'image_url': image_url,
        'image_processed': image_processed
    })



from django.shortcuts import render
from .models import FoodItem
from datetime import datetime, date, timedelta
from django.shortcuts import render
from .models import FoodItem
from datetime import date, timedelta, datetime

from django.shortcuts import render
from .models import FoodItem
from datetime import date, timedelta, datetime

def dashboard(request):
    food_items = FoodItem.objects.all()  # Fetch all food items from the database

    # Adding static status based on expiry date
    for item in food_items:
        # Ensure expiry_date is a datetime.date object (this will work if it's a DateField)
        if isinstance(item.expiry_date, str):
            # If it's a string, try converting it to a datetime.date
            try:
                # Attempt to parse the date string with the correct format
                item.expiry_date = datetime.strptime(item.expiry_date, '%d %b %Y').date()
            except ValueError:
                # Handle incorrect format, if necessary, or log an error
                item.expiry_date = None
        
        if item.expiry_date:
            if item.expiry_date < date.today():
                item.status = 'expired'
            elif item.expiry_date < (date.today() + timedelta(days=7)):
                item.status = 'expiring soon'
            else:
                item.status = 'good'
        else:
            item.status = 'invalid date'  # If the date couldn't be parsed

    return render(request, 'user/dashboard.html', {'food_items': food_items})



def recipee_slider(request):
    return render(request, 'user/recipee_slider.html')


# views.py

from django.shortcuts import render
from django.http import StreamingHttpResponse
from ultralytics import YOLO
import cv2
import numpy as np
from twilio.rest import Client
import os 


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_twilio_notification():
    message_text = "🍌 Alert! Your banana has started rotting! 🍌 Consider making a recipe today! 😋"

    client.messages.create(
        from_='whatsapp:+14155238886',
        body=message_text,
        to='whatsapp:+918657689680'
    )

    image_url = 'https://static.toiimg.com/thumb/msid-67569905,width-400,resizemode-4/67569905.jpg'
    client.messages.create(
        from_='whatsapp:+14155238886',
        media_url=[image_url],
        body="Here's a recipe suggestion! 🍌🥛",
        to='whatsapp:+918657689680'
    )

def gen_frames():
    # Initialize the YOLO model and specify the device explicitly
    model = YOLO("yolov8n.pt")
    model.to('cpu')  # Ensure it's running on CPU (replace with 'cuda' for GPU)
    
    cap = cv2.VideoCapture("banana2.mp4")
    start_rotting_threshold = 0.1
    fully_rotted_threshold = 0.2
    notification_sent = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)  # Get the predictions from YOLO model
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detected_area = frame[y1:y2, x1:x2]

                gray = cv2.cvtColor(detected_area, cv2.COLOR_BGR2GRAY)
                _, black_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
                
                black_ratio = np.sum(black_mask == 255) / black_mask.size

                if black_ratio > fully_rotted_threshold:
                    stage = "Rotted"
                elif black_ratio > start_rotting_threshold:
                    stage = "Started Rotting"
                    if not notification_sent:
                        pass
                        # send_twilio_notification()
                        # notification_sent = True
                else:
                    stage = "Good"

                cv2.putText(frame, "Banana", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Stage: {stage}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()

def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def rotting_index(request):
    return render(request, 'user/rotting.html')
