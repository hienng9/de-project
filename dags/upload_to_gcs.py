from google.cloud import storage

def upload_to_gcs(bucket, object_name, local_file):
  storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024
  storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024

  client = storage.Client()
  bucket = client.bucket(bucket)

  blob = bucket.blob(object_name)
  blob.upload_from_filename(local_file)