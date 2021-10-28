import os
from init_object_detection import init_object_detection
from init_auto_text_filter import init_auto_text_filter
from init_match_image import init_match_image

if __name__ == "__main__":
    service_type = os.environ.get('SERVICE_TYPE','all')
    print("Ready to initialize the service : {}".format(service_type))
    if service_type in ["all", "object-detection"]:
        print("Start to initialize the service : {}".format(service_type))
        init_object_detection()
        print("Complete initialization service : {}".format(service_type))
    if service_type in ["all", "auto-text-filter"]:
        print("Start to initialize the service : {}".format(service_type))
        init_auto_text_filter()
        print("Complete initialization service : {}".format(service_type))
    if service_type in ["all", "match-image"]:
        print("Start to initialize the service : {}".format(service_type))
        init_match_image()
        print("Complete initialization service : {}".format(service_type))
