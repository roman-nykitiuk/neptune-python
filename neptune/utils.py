import time


def make_imagefield_filepath(upload_to, instance, filename):
    model_class = instance.__class__
    uploading_filename = f'{upload_to}/{filename}'

    while model_class.objects.filter(image=uploading_filename).exists():
        file_parts = uploading_filename.split('.')
        file_extension = file_parts.pop()
        file_name = '.'.join(file_parts)
        timestamp = int(time.time())
        uploading_filename = f'{file_name}-{timestamp}.{file_extension}'

    return uploading_filename
