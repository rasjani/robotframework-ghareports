*** Settings ***


*** Test Cases ***

This will just be for debugging purposes
  Should Be Equal   ${True}   ${False}    This Suite will completely fail with assertation

And so is this
  Sleep   2 seconds
  Fail    This Suite will completely fail

Yet An Another Warning
  Log   Another warning, pay attention    WARN
