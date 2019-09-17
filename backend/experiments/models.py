# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Animal(models.Model):
  """
  A mouse that performs sessions.
  """
  id = models.CharField(primary_key=True, max_length=64)
  genotype = models.CharField(max_length=64) 


class Session(models.Model):
  """
  A grouping of Trials for a given animal on a given day.
  """
  id = models.AutoField(primary_key=True)

  date = models.DateField(auto_now_add=True)

  animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
  
  # TODO: should we enforce choices here or only on the ui side
  box_number = models.CharField(max_length=10)

  tier = models.IntegerField()#choices=(1, 2, 3))

  optogenetics = models.CharField(max_length=30)
  #  choices=('NONE', 'ACTIVATION', 'SUPRESSION')
  #)
  #mW = models.FloatField(null=True)
  background_lum = models.IntegerField()

  # TODO: make this a sizes list
  size_one = models.IntegerField()
  size_two = models.IntegerField(null=True)
  # TODO: figure out list fields
  # contrast_levels = models.ArrayField()


class Trial(models.Model):
  """
  A short trial in which an animal is shown a stimulus and then
  may or may not respond.
  """
  id = models.AutoField(primary_key=True)
  session = models.ForeignKey(Session, on_delete=models.CASCADE)
  trialNumber = models.IntegerField()

  # Stim parameters.
  contrast = models.IntegerField()
  stim_size = models.IntegerField()

  is_optogenetics = models.BooleanField()

  # Animal responses
  is_licked = models.BooleanField()
  response_time = models.IntegerField()


class DataPoint(models.Model):
  id = models.AutoField(primary_key=True)
  trial = models.ForeignKey(Trial, on_delete=models.CASCADE)

  timestamp = models.IntegerField()

  # Trial events.
  is_stim = models.BooleanField()
  is_port_open = models.BooleanField()
  is_tone = models.BooleanField()
  is_led_on = models.BooleanField()

  # Animal behaviors.
  is_licking = models.BooleanField()
  is_false_alarm = models.BooleanField()


