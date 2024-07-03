from django.db import models

class IDSProductDetails(models.Model):
    productId = models.CharField(max_length=20, primary_key=True)
    category = models.TextField()
    item = models.TextField()
    description = models.TextField()
    units = models.CharField(max_length=100)
    thresholdValue = models.IntegerField()
    images = models.JSONField(default=list)  # To store multiple image URLs or paths
    class Meta:
        permissions = [
            ('can_view_all_products', 'Can view all products'),
        ]

    def __str__(self):
        return self.item