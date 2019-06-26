import PIL.ImageFont
import os
from datetime import datetime

def get_current_image_file_name(camera_name):
    now = datetime.now()
    date = now.strftime("%Y.%m.%d")    
    current_time = now.strftime("%H:%M:%S:%f")
    image_folder = 'images/{}/{}'.format(camera_name, date)	        
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)      
    return '{}/{}.jpg'.format(image_folder, current_time)    
    




