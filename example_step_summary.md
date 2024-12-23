
---
# Totals

| Passed ✅ | Failed ❌ | Skipped ⏩ | Total | Passrate % | Duration (sec) |
|:--------:|:--------:|:---------:|:-----:|-----------:|---------------:|
| 6 |4 |1 |11 |54.55 |4.1 |

# ✅ Passing tests

| Testcase | Duration (sec) | Suite |
|:---------|---------------:|:------|
| Third Test With maybe longer name |1.0 |Example.Multiple Suites.Secondary Suite |
| Fourth suite and we still want something more to debug |0.5 |Example.Multiple Suites.Secondary Suite |
| Yet An Another Warning |0.0 |Example.Multiple Suites.Ternary Suite |
| First Test |0.2 |Example.Single Suite.Initial Suite |
| Issue a Warning |0.0 |Example.Single Suite.Initial Suite |
| Issue Multiple Warnings From FOR loop |0.0 |Example.Single Suite.Initial Suite |

# ❌ Failing tests

| Testcase | Message | Duration (sec) | Suite |
|:---------|:--------|---------------:|:------|
| This will just be for debugging purposes |This Suite will completely fail with assertation: True != False |0.0 |Example.Multiple Suites.Ternary Suite |
| And so is this |This Suite will completely fail |2.0 |Example.Multiple Suites.Ternary Suite |
| Second Test |For the heck of it, lets mark this case as failure |0.3 |Example.Single Suite.Initial Suite |
| Forth Test With Very Long Message |TimeoutError: page.waitForNavigation: Timeout 10000ms exceeded.<br/>=========================== logs ===========================<br/>waiting for navigation to |0.0 |Example.Single Suite.Initial Suite |

# ⏩ Skipped tests

| Testcase | Message | Duration (sec) | Suite |
|:---------|:--------|---------------:|:------|
| Third One Is Skipped |This Test Will Be Skipped |0.0 |Example.Single Suite.Initial Suite |

# ⚠ Warnings

| Test Case | Message | Suite |
|:----------|:--------|:------|
| This will just be for debugging purposes |Here We Print Out A Variable; This Is A String |Example.Multiple Suites.Ternary Suite |
| Yet An Another Warning |Another warning, pay attention |Example.Multiple Suites.Ternary Suite |
| Issue a Warning |Warning to all rudeboys and rudegals! |Example.Single Suite.Initial Suite |
| Issue Multiple Warnings From FOR loop |Warning Step: one |Example.Single Suite.Initial Suite |
| Issue Multiple Warnings From FOR loop |Warning Step: two |Example.Single Suite.Initial Suite |
| Issue Multiple Warnings From FOR loop |Warning Step: three |Example.Single Suite.Initial Suite |

