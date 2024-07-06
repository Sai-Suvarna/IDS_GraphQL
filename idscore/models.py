from django.db import models
from django.contrib.postgres.fields import ArrayField


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    image = models.URLField(null=True, blank=True)  # Store image as URL
    rowstatus = models.BooleanField(default=True)

class Product(models.Model):
    productid = models.AutoField(primary_key=True)
    productcode = models.CharField(max_length=100)
    qrcode = models.TextField()
    productname = models.CharField(max_length=255)
    productdescription = models.TextField()
    productcategory = models.IntegerField()
    reorderpoint = models.IntegerField()
    brand = models.CharField(max_length=100)
    weight = models.CharField(max_length=50)
    dimensions = models.CharField(max_length=100)
    images = models.JSONField()
    # image = models.BinaryField(null=True, blank=True) 
    createduser = models.CharField(max_length=100)
    modifieduser = models.CharField(max_length=100)
    createdtime = models.DateTimeField(auto_now_add=True)
    modifiedtime = models.DateTimeField(auto_now=True)
    rowstatus = models.BooleanField(default=True)

    def __str__(self):
        return self.productname



class Inventory(models.Model):
    inventoryid = models.AutoField(primary_key=True)
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantityavailable = models.CharField(max_length=50)
    minstocklevel = models.CharField(max_length=50)
    maxstocklevel = models.CharField(max_length=50)
    reorderpoint = models.IntegerField()
    warehouseid = models.ForeignKey('Warehouse', on_delete=models.CASCADE)
    createduser = models.CharField(max_length=100)
    modifieduser = models.CharField(max_length=100)
    createdtime = models.DateTimeField(auto_now_add=True)
    modifiedtime = models.DateTimeField(auto_now=True)
    rowstatus = models.BooleanField(default=True)

    def __str__(self):
        return f"Inventory for {self.productid.productname}"



class Warehouse(models.Model):
    warehouseid = models.AutoField(primary_key=True)
    locationid = models.ForeignKey('Location', on_delete=models.CASCADE)
    warehousename = models.CharField(max_length=255)
    createduser = models.CharField(max_length=100)
    modifieduser = models.CharField(max_length=100)
    createdtime = models.DateTimeField(auto_now_add=True)
    modifiedtime = models.DateTimeField(auto_now=True)
    rowstatus = models.BooleanField(default=True)

    def __str__(self):
        return self.warehousename



class Location(models.Model):
    locationid = models.AutoField(primary_key=True)
    locationname = models.CharField(max_length=255)
    locationaddress = models.TextField()
    createduser = models.CharField(max_length=100)
    modifieduser = models.CharField(max_length=100)
    createdtime = models.DateTimeField(auto_now_add=True)
    modifiedtime = models.DateTimeField(auto_now=True)
    rowstatus = models.BooleanField(default=True)

    def __str__(self):
        return self.locationname
    

class Batch(models.Model):
    batchid = models.AutoField(primary_key=True)
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)
    manufacturedate = models.DateField()
    expirydate = models.DateField()
    quantity = models.CharField()
    createduser = models.CharField(max_length=100)
    modifieduser = models.CharField(max_length=100)
    createdtime = models.DateTimeField(auto_now_add=True)
    modifiedtime = models.DateTimeField(auto_now=True)
    rowstatus = models.BooleanField(default=True)

    def __str__(self):
        return f'Batch {self.batchid} for {self.productid}'
    

class Placement(models.Model):
    placementId = models.AutoField(primary_key=True)
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouseid = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    aile = models.CharField(max_length=50)  
    bin = models.CharField(max_length=50)   
    batchid = models.ForeignKey(Batch, on_delete=models.CASCADE)
    createduser = models.CharField(max_length=100)
    modifieduser = models.CharField(max_length=100)
    createdtime = models.DateTimeField(auto_now_add=True) 
    modifiedtime = models.DateTimeField(auto_now=True)
    rowstatus = models.BooleanField(default=True)

    def __str__(self):
        return f'Placement {self.placementId} - Product: {self.productid}, Warehouse: {self.warehouseid}'
