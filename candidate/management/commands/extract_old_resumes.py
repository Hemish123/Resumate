# import os
# from django.core.management.base import BaseCommand
# from django.core.files.base import ContentFile
# from django.conf import settings
# from candidate.models import Candidate
# from adminuser.utils import extract_resume_text

# from azure.storage.blob import BlobServiceClient


# class Command(BaseCommand):
#     help = "Extract text from old Azure resumes and save into text_content"

#     def handle(self, *args, **kwargs):

#         self.stdout.write(self.style.SUCCESS("Starting extraction process..."))

#         # ✅ Azure Connection
#         account_name = os.environ.get("AZURE_ACCOUNT_NAME")
#         account_key = os.environ.get("AZURE_ACCOUNT_KEY")

#         if not account_name or not account_key:
#             self.stdout.write(self.style.ERROR("Azure credentials not found"))
#             return

#         connect_str = (
#             f"DefaultEndpointsProtocol=https;"
#             f"AccountName={account_name};"
#             f"AccountKey={account_key};"
#             f"EndpointSuffix=core.windows.net"
#         )

#         blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#         container_client = blob_service_client.get_container_client("media")

#         # ✅ Only old resumes (no text_content)
#         candidates = Candidate.objects.filter(
#             upload_resume__isnull=False
#         ).filter(
#             text_content__isnull=True
#         ) | Candidate.objects.filter(
#             upload_resume__isnull=False,
#             text_content=""
#         )

#         total = candidates.count()

#         if total == 0:
#             self.stdout.write(self.style.SUCCESS("No old resumes found 🎉"))
#             return

#         self.stdout.write(self.style.WARNING(f"Found {total} resumes to process"))

#         processed = 0

#         # for candidate in candidates:
#         #     try:
#         #         full_url = candidate.upload_resume.name

#         #         import urllib.parse
#         #         parsed_url = urllib.parse.urlparse(full_url)
#         #         path_parts = parsed_url.path.lstrip("/").split("/", 1)
#         #         if len(path_parts) != 2:
#         #             self.stdout.write(self.style.WARNING(f"Invalid blob URL for {candidate.name}"))
#         #             continue

#         #         container_name, blob_name = path_parts

#         #         container_client = blob_service_client.get_container_client(container_name)
#         #         blob_client = container_client.get_blob_client(blob=blob_name)

#         #         download_stream = blob_client.download_blob()
#         #         file_bytes = download_stream.readall()

#         #         file_obj = ContentFile(file_bytes)
#         #         file_obj.name = blob_name

#         #         extracted_text = extract_resume_text(file_obj)

#         #         if extracted_text:
#         #             candidate.text_content = extracted_text
#         #             candidate.save(update_fields=["text_content"])
#         #             self.stdout.write(self.style.SUCCESS(f"Processed: {candidate.name}"))
#         #         else:
#         #             self.stdout.write(self.style.WARNING(f"No text found: {candidate.name}"))

#         #     except Exception as e:
#         #         self.stdout.write(self.style.ERROR(f"Error processing {candidate.name}: {str(e)}"))
#         for candidate in candidates:
#             try:
#                 blob_name = candidate.upload_resume.name
        
#                 blob_client = container_client.get_blob_client(blob=blob_name)
        
#                 download_stream = blob_client.download_blob()
#                 file_bytes = download_stream.readall()
        
#                 file_obj = ContentFile(file_bytes)
#                 file_obj.name = blob_name
        
#                 extracted_text = extract_resume_text(file_obj)
        
#                 if extracted_text:
#                     candidate.text_content = extracted_text
#                     candidate.save(update_fields=["text_content"])
#                     processed += 1
#                     self.stdout.write(self.style.SUCCESS(f"Processed: {candidate.name}"))
#                 else:
#                     self.stdout.write(self.style.WARNING(f"No text found: {candidate.name}"))
        
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f"Error processing {candidate.name}: {str(e)}"))


#         self.stdout.write(
#             self.style.SUCCESS(f"\nExtraction completed. {processed}/{total} updated.")
#         )

# import os

# from django.core.management.base import BaseCommand
# from django.core.files.base import ContentFile

# from candidate.models import Candidate
# from adminuser.utils import extract_resume_text

# from azure.storage.blob import BlobServiceClient


# class Command(BaseCommand):

#     help = "Extract text from Azure resumes"

#     def handle(self, *args, **kwargs):

#         print("Starting extraction...")

#         account_name = os.environ.get("AZURE_ACCOUNT_NAME")
#         account_key = os.environ.get("AZURE_ACCOUNT_KEY")

#         connect_str = (
#             f"DefaultEndpointsProtocol=https;"
#             f"AccountName={account_name};"
#             f"AccountKey={account_key};"
#             f"EndpointSuffix=core.windows.net"
#         )

#         blob_service_client = BlobServiceClient.from_connection_string(connect_str)

#         container_client = blob_service_client.get_container_client("media")

#         candidates = Candidate.objects.exclude(
#             upload_resume=""
#         ).exclude(
#             upload_resume__isnull=True
#         )

#         total = candidates.count()

#         print("Total resumes:", total)

#         processed = 0

#         for candidate in candidates.iterator(chunk_size=50):

#             try:

#                 blob_name = str(candidate.upload_resume)

#                 print("Downloading:", blob_name)

#                 blob_client = container_client.get_blob_client(blob=blob_name)

#                 download_stream = blob_client.download_blob()

#                 file_bytes = download_stream.readall()

#                 file_obj = ContentFile(file_bytes)
#                 file_obj.name = blob_name

#                 extracted_text = extract_resume_text(file_obj)

#                 if extracted_text:

#                     candidate.text_content = extracted_text
#                     candidate.save(update_fields=["text_content"])

#                     processed += 1

#                     print("Processed:", candidate.id)

#             except Exception as e:

#                 print("Error:", candidate.id, e)

#         print("Finished. Processed:", processed)

import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from azure.storage.blob import BlobServiceClient

from candidate.models import Candidate
from adminuser.utils import extract_resume_text


class Command(BaseCommand):

    help = "Extract text from Azure blob resumes only"

    def handle(self, *args, **kwargs):

        print("Starting Azure resume extraction...")

        account_name = os.environ.get("AZURE_ACCOUNT_NAME")
        account_key = os.environ.get("AZURE_ACCOUNT_KEY")

        connect_str = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account_name};"
            f"AccountKey={account_key};"
            f"EndpointSuffix=core.windows.net"
        )

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        container_client = blob_service_client.get_container_client("media")

        # ONLY FETCH RESUMES FOLDER
        blobs = list(container_client.list_blobs(name_starts_with="resumes/"))

        total = len(blobs)

        print("Total Azure resumes:", total)

        processed = 0

        for blob in blobs:

            try:

                blob_name = blob.name

                blob_client = container_client.get_blob_client(blob_name)

                download_stream = blob_client.download_blob()

                file_bytes = download_stream.readall()

                file_obj = ContentFile(file_bytes)
                file_obj.name = blob_name

                extracted_text = extract_resume_text(file_obj)

                if not extracted_text:
                    continue

                # find candidate with this resume
                candidate = Candidate.objects.filter(
                    upload_resume=blob_name
                ).first()

                if candidate:

                    candidate.text_content = extracted_text
                    candidate.save(update_fields=["text_content"])

                    processed += 1

                    print("Processed:", candidate.id)

            except Exception as e:

                print("Error:", blob.name, str(e))

        print("Extraction completed:", processed)
