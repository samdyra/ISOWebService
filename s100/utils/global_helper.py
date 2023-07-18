import random
import string

def generate_random_filename(file_name):
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    new_file_name = f"{file_name}-{random_string}"
    return new_file_name
