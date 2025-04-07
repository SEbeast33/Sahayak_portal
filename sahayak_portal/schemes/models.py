from django.db import models

class Scheme(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    ministry = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100)
    category = models.CharField(max_length=255)
    gender = models.CharField(max_length=50, null=True, blank=True)
    age_group = models.CharField(max_length=100, null=True, blank=True)
    caste = models.CharField(max_length=255, null=True, blank=True)
    residence = models.CharField(max_length=255, null=True, blank=True)
    minority = models.BooleanField(default=False)
    differently_abled = models.BooleanField(default=False)

    benefit_type = models.TextField(null=True, blank=True)  # changed
    eligibility_criteria = models.TextField(null=True, blank=True)  # changed
    documents_required = models.TextField(null=True, blank=True)  # changed
    tags = models.TextField(null=True, blank=True)  # changed

    language = models.CharField(max_length=10, default='en')
    url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
class Feedback(models.Model):
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_text = models.TextField()
    rating = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback on {self.scheme.title} - {self.rating}"
