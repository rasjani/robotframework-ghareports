*** Keywords ***
Test Case Template
  [Arguments]   ${arg1}
  Log To Console    This Is Test Case Template
  ${var}=   Set Variable    Test Case Template
  Log         Issued Warning From ${var} with arg ${arg1}    warn
  [Teardown]    Test Case Teardown


Test Case Setup
  ${var1}=   Set Variable    Test Case Setup
  Log         Issued Warning From ${var1}    warn



Test Case Teardown
  ${var2}=   Set Variable    Test Case Teardown
  ${var3}=   Set Variable    Can I Repro?
  Log         Issued Warning From ${var2}.${var3}    warn
