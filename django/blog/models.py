from django.db import models

class Post(models.Model):
    title = models.CharField(max_length = 140)
    body = models.TextField()
    date = models.DateTimeField()

    # returns title as a string rather than "post object at <<x023240"
    def __str__(self):
        return self.title