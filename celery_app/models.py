from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)
    born = models.TextField(default='NA')
    description = models.TextField(default='NA')

    def __str__(self):
        return self.name


class Quote(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='quotes')
    content = models.TextField()

    def __str__(self):
        return self.content

# Create your models here.
