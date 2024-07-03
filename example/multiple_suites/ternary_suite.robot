*** Settings ***


*** Test Cases ***

This will just be for debugging purposes
  [Teardown]     Log Something In Teardown
  Should Be Equal   ${True}   ${False}    This Suite will completely fail with assertation

And so is this
  Sleep   2 seconds
  Fail    This Suite will completely fail

Yet An Another Warning
  Log   Another warning, pay attention    WARN


*** Keywords ***
Log Something In Teardown
  ${somestring}=    Set Variable    This Is A String
  Log   Here We Print Out A Variable; ${somestring}   WARN
