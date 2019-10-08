# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 

"""
session_info  = {

  'opto_params': {
    'do_opto': False,
    'mW': 0,
    'nominal mW': 0,
    'dist_above': 0,
    'non_opto_weight': 2,
  }
  'training_params': {
    'tier': 1,
    'stim_sets': #all stim sets with that foreign key
  }
}

"""

class Animal(models.Model):
  """
  A mouse that performs sessions.
  """
  id = models.CharField(primary_key=True, max_length=64)
  ear_tag = models.CharField(max_length=10)
  genotype = models.CharField(max_length=64) 
  date_of_birth = models.DateField(auto_now_add=False)
  training_start = models.DateField(auto_now_add=True)
  sex = models.CharField(max_length=1)


class Session(models.Model):
  """
  A grouping of Trials for a given animal on a given day.
  """
  id = models.AutoField(primary_key=True)

  date = models.DateTimeField(auto_now_add=True)

  animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
  
  # TODO: should we enforce choices here or only on the ui side
  box_number = models.CharField(max_length=10)

  # training vars
  tier = models.IntegerField(
    validators = [MinValueValidator(1), MaxValueValidator(4)]
    )
  background_lum = models.IntegerField(
       validators = [MinValueValidator(0), MaxValueValidator(128)]
    ) 

  #exp timing params, in ms
  stim_delay = models.IntegerField(default=0) 
  stim_time = models.IntegerField(default=500) 
  response_window = models.IntegerField(default=1000) 
  isi_min = models.IntegerField(default=3000)
  isi_max = models.IntegerField(default=8000)
  grace_time = models.IntegerField(default=1000)
  valve_open_time = models.IntegerField(default=20)

  #optogenetic_vars
  #TODO: implement these
  optogenetics = models.CharField(max_length=30,
    choices=(
      ('N','NONE'),
      ('A','ACTIVATION'),
      ('S', 'SUPRESSION'))
  )
  #mW = models.FloatField(null=True)

class StimSet(models.Model):
  """
  a class of stimuli with a single set of properties
  and experimental meaning, but can have many contrasts.
  Each contrast has its own weight.
  Belongs to a session
  """
  id = models.AutoField(primary_key=True)
  session = models.ForeignKey(Session, on_delete=models.CASCADE)

  #weight relative to other stim sets
  overall_weight = models.PositiveIntegerField(default=1)

  #stim params
  spatial_freq = models.FloatField(default=.08) #cpd
  temporal_freq = models.FloatField(default=2) #Hz
  position_x = models.FloatField(default=0) #deg
  position_y = models.FloatField(default=0) #deg
  stim_size = models.IntegerField()
  orientation = models.PositiveIntegerField(
    default=225,
    validators=[MaxValueValidator(360)]
    )

  #contrast and contrast weights
  #TODO! Can't Decide

  should_lick = models.BooleanField()





class Trial(models.Model):
  """
  A short trial in which an animal is shown a stimulus and then
  may or may not respond.
  TODO: make this log more of the actual trial fields
  """
  id = models.AutoField(primary_key=True)
  session = models.ForeignKey(Session, on_delete=models.CASCADE)
  trial_number = models.IntegerField()

  # Stim parameters.
  contrast = models.IntegerField()
  stim_size = models.IntegerField()

  is_optogenetics = models.BooleanField()

  # Animal responses
  is_licked = models.BooleanField(null=True)
  response_time = models.IntegerField(null=True)


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


