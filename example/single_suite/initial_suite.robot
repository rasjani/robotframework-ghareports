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

Forth Test With Very Long Message
  Fail    TimeoutError: page.waitForNavigation: Timeout 10000ms exceeded.\n=========================== logs ===========================\nwaiting for navigation to
  "https://dev-prepaid.telia.io/fi/account/signup/otp" until "load"\n============================================================\nTip: Use "Set Browser Timeout" for increasing the timeout.
