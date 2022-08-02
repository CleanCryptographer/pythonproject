from django.db import models

# Create your models here.


class FlightData(models.Model):
    flightCode = models.CharField(max_length=100)
    leavingCityCode = models.CharField(max_length=100)
    landingCityCode = models.CharField(max_length=100)
    leavingDateTimeUTC = models.CharField(max_length=100)
    landingDateTimeUTC = models.CharField(max_length=100)
    leavingDate = models.CharField(max_length=100)
    landingDate = models.CharField(max_length=100)
    leavingTime = models.CharField(max_length=100)
    landingTime = models.CharField(max_length=100)

    class Meta:
        managed = False
