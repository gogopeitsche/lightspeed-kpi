import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

EMAIL_ID = "854f644c-be3e-4bdf-ab23-fcdd1125750b"

print(dir(resend.emails.receiving))
