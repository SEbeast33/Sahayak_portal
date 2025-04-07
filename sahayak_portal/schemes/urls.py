from django.urls import path
from .views import (
    fetch_all_schemes,
    fetch_by_filters,
    fetch_by_uid,
    search_schemes,
    feedback_api,
    health_check
)

urlpatterns = [
    path('api/schemes/', fetch_all_schemes, name='scheme-list'),
    path('api/schemes/filter/', fetch_by_filters, name='scheme-filter'),
    path('api/schemes/<int:scheme_id>/', fetch_by_uid, name='scheme-detail'),
    path('api/schemes/search/', search_schemes, name='scheme-search'),
    path('api/feedback/', feedback_api, name='feedback-create'),
    path('api/health/', health_check, name='health-check'),
]
