import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import RequestFactory
from analytics.views import AnalyticsViewSet
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

factory = RequestFactory()
request = factory.get('/api/analytics/download-report/?month=3&year=2026')
request.user = user

view = AnalyticsViewSet.as_view({'get': 'download_report'})
response = view(request)

if response.status_code == 200:
    # Check if it has PDF content type
    print("Status:", response.status_code)
    print("Content-Type:", response['Content-Type'])
    print("Content-Disposition:", response['Content-Disposition'])
    
    with open('test_report.pdf', 'wb') as f:
        f.write(response.content)
    print("PDF generated successfully and saved to test_report.pdf")
else:
    print(f"Error: {response.status_code}")
    try:
        print(response.content)
    except Exception as e:
        print("Could not print content:", str(e))
