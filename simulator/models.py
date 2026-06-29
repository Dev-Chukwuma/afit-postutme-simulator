from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

COURSE_CHOICES = [
    ('Computer Science', 'Computer Science'),
    ('Electrical Engineering', 'Electrical Engineering'),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Civil Engineering', 'Civil Engineering'),
    ('Physics', 'Physics'),
    ('Mathematics', 'Mathematics'),
    
]

SUBJECT_CHOICES = [
    ('Mathematics', 'Mathematics'),
    ('English', 'English'),
    ('Chemistry', 'Chemistry'),
    ('Physics', 'Physics'),
    ('Computer Science', 'Computer Science'),
    ('Electrical Engineering', 'Electrical Engineering'),
    ('Mechanical Engineering', 'Mechanical Engineering'),
    ('Civil Engineering', 'Civil Engineering'),
    # Add more course-specific subjects here
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    jamb_score = models.IntegerField()
    aspiring_course = models.CharField(max_length=100, choices=COURSE_CHOICES)

    def __str__(self):
        return self.full_name


class Question(models.Model):
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES)
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    correct_answer = models.CharField(max_length=1)  
    order = models.IntegerField(default=0)  
    @property
    def options(self):
        return[
            ('A', self.option_a),
            ('B', self.option_b),
            ('C', self.option_c),
            ('D', self.option_d),
        ]
    class Meta:
        ordering = ['order']  # always fetch in order

    def __str__(self):
        return f"{self.subject} - {self.question_text[:50]}"


import json
from django.db import models
from django.contrib.auth.models import User

class ExamResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    postutme_score = models.IntegerField()
    aggregate = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)
    review_data = models.TextField(blank=True, default='')

    def get_review(self):
        if self.review_data:
            return json.loads(self.review_data)
        return []

    def __str__(self):
        return f"{self.user.username} - {self.aggregate}"