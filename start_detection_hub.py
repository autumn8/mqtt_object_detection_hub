import numpy as np
import paho.mqtt.client as mqtt
import cv2
import json
import time
import os
from utils import get_current_image_file_name
from PIL import Image
from edgetpu.detection.engine import DetectionEngine
from imutils.video import VideoStream
from render_detection_box import draw_obj_bounding_box, draw_detection_zone

#variables
frame = None
model = "mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite"
cameras = {}
frame_detection_active = False
last_frame_incident_time = 0
event_time_interval = 60
PERSON = 0 #coco class id.

def on_message(client, userdata, msg):
	global cameras
	global frame
	if 'camera/connected/' in msg.topic:				
		payload = msg.payload.decode("utf-8") 
		camera_name = msg.topic.split('/')[-1] 		
		print("camera connected" + camera_name + '. payload: ' + payload)					
		if payload == 'True':										
			client.subscribe("camera/settingsupdate/" + camera_name) 
					
	elif 'camera/settingsupdate/' in msg.topic:		
		payload = msg.payload.decode("utf-8")
		camera_name = msg.topic.split('/')[-1]
		camera_settings = json.loads(payload)		
		cameras[camera_name] = camera_settings
		client.subscribe("camera/frame/" + camera_name) 		

	elif 'camera/frame/' in msg.topic:				
		camera_name = msg.topic.split('/')[-1]						
		frame = cv2.imdecode(np.fromstring(msg.payload, dtype='uint8'), -1)	
		camera_settings = cameras[camera_name]			
		if camera_settings['isDetectionEnabled'] is True: 			
			process_frame(frame, camera_settings)
		#cv2.imshow('Detection:{}'.format(camera_name), frame)	

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("camera/connected/#") 	

def set_last_frame_incident_time(time):
	global last_frame_incident_time
	last_frame_incident_time = time

def is_new_incident(time_since_last_frame_detection):
	return time_since_last_frame_detection > event_time_interval

def process_frame_detection_event(camera_name):	
	current_time = int(time.time())	
	time_since_last_frame_detection = current_time - last_frame_incident_time 	
	if is_new_incident(time_since_last_frame_detection):  
		print(camera_name)
		print('person detected in frame. Send mqtt message!')	
		client.publish('camera/detection/frame/{}'.format(camera_name), json.dumps({"detection" : True}))			
		set_last_frame_incident_time(current_time)

def save_file(frame, camera_name):	
	image_file_name = get_current_image_file_name(camera_name)	
	cv2.imwrite(image_file_name, frame) 

def process_frame(frame, camera_settings):									          
	inference_image = Image.fromarray(frame)           
	detection_results = engine.DetectWithImage(inference_image, threshold=0.5, keep_aspect_ratio=True, relative_coord=False, top_k=5)	
	draw_detection_zone(frame, camera_settings)				
	for obj in detection_results: 		
		if(obj.label_id is not PERSON): continue								         
		draw_obj_bounding_box(frame, obj)
		process_frame_detection_event(camera_settings['name'])		
		save_file(frame, camera_settings['name'])
		break	

 #init  
#vs = VideoStream(usePiCamera=True, resolution=(320, 240)).start()
time.sleep(1)    

engine = DetectionEngine(model)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.8.202", 1883, 60)
time.sleep(1) 	
		 
while True:
	client.loop()	
	#if cv2.waitKey(1)&0xFF == ord('q'):
	#	break
		
#cv2.destroyAllWindows()
time.sleep(2)
