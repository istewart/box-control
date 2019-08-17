# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Animal(models.Model):
  """
  A mouse that performs sessions.
  """
  id = models.CharField(primary_key=True)
  genotype = models.CharField() 


class Session(models.Model):
  """
  A grouping of Trials for a given animal on a given day.
  """
  id = models.AutoField(primary_key=True)

  date = models.DateField()

  animal = models.ForeignKey(Animal)
  box_number = models.IntegerField()
  stage = models.ChoiceField(choices=(1, 2, 3))

  optogenetics = models.ChoiceField(
    choices=('NONE', 'ACTIVATION', 'SUPRESSION')
  )
  background_luminensce = models.IntegerField()
  size_one = models.IntegerField()
  size_two = models.IntegerField(null=True)
  contrast_levels = models.ArrayField()


class Trial(models.Model):
  """
  A short trial in which an animal is shown a stimulus and then
  may or may not respond.
  """
  id = models.AutoField(primary_key=True)
  session = models.ForeignKey(Session)

  # Stim parameters.
  intensity = models.IntegerField()
  stim_size = models.IntegerField()

  is_optogenetics = models.BooleanField()


class DataPoint(models.Model):
  id = models.AutoField(primary_key=True)
  trial = models.ForeignKey(Trial)

  timestamp = models.DateTimeField()

  # Trial events.
  is_stim = models.BooleanField()
  is_port_open = models.BooleanField()
  is_rewarded = models.BooleanField()
  is_tone = models.BooleanField()

  # Animal behaviors.
  is_licking = models.BooleanField()
  is_false_alarm = models.BooleanField()


