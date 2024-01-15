*** Settings ***


*** Test Cases ***

First Test
  Log To Console    Here's some output
  Sleep   0.2 seconds
  No Operation

Second Test
  Sleep   0.3 seconds
  Fail    For the heck of it, lets mark this case as failure

Third One Is Skipped
  Skip    This Test Will Be Skipped
