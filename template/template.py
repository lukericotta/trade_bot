"""
Template
"""

import datetime
import enum
import logging

class Template():
  """
  Template

  Args:
    string: text
    int: integer
  """
  def __init__(self, string, int):
    self.string = string
    self.int = int
