from django.utils.deprecation import MiddlewareMixin 
import threading
import time
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LogRequestMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
        self.attack_log = []

        self.running = True
        self.thread = threading.Thread(target=self.background_ddos_detection)
        self.thread.start()

        

    def __del__(self):
        self.running = False
        self.thread.join()
        

    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        current_time = time.time()
      

        with self.lock:
            self.requests[client_ip].append(current_time)
            # Remove requests older than 60 seconds
            self.requests[client_ip] = [t for t in self.requests[client_ip] if current_time - t < 60]

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
     
        return ip

    def background_ddos_detection(self):
        while self.running:
            time.sleep(2)
            current_time = time.time()
            with self.lock:
                for client_ip, timestamps in list(self.requests.items()):
                    self.requests[client_ip] = [t for t in timestamps if current_time - t < 60]
                    if len(self.requests[client_ip]) > 1:  # Adjust threshold as needed
                        self.log_ddos_attack(client_ip, len(self.requests[client_ip]))

    def log_ddos_attack(self, ip, request_count):
        log_message = f"Attack detected on {ip} with {request_count} requests per minute\n"
        with open('ddos_log.txt', 'a') as log_file:
            log_file.write(log_message)
 
