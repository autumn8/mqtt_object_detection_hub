import cv2

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.4
box_color = (255, 128, 0)
box_thickness = 1
font_color = (255, 255, 255)


def draw_obj_bounding_box_text(video_frame, x, y, score):      
	confidence =  str(int(score * 100)) 	
	label_text = "{}:{}%".format('Person', confidence) 
	cv2.putText(video_frame, label_text, (x + 5, y + 10), font, font_scale, font_color, 1)  
	
def draw_obj_bounding_box(video_frame, obj):          
	start_x, start_y, end_x, end_y = obj.bounding_box.flatten().astype("int") 
	obj.bounding_box.flatten().astype("int")                  
	cv2.rectangle(video_frame, (start_x, start_y), (end_x, end_y), box_color, box_thickness)
	draw_obj_bounding_box_text(video_frame, start_x, start_y, obj.score)


