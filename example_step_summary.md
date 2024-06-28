
---
# Totals

| Passed ✅ | Failed ❌ | Skipped ⏩ | Total | Passrate % | Duration (sec) |
|:--------:|:--------:|:---------:|:-----:|-----------:|---------------:|
| 5 |4 |1 |10 |50.0 |4.1 |

# ✅ Passing tests

| Testcase | Duration (sec) | Suite |
|:---------|---------------:|:------|
| Third Test With maybe longer name |1.0 |Example.Multiple Suites.Secondary Suite |
| Fourth suite and we still want something more to debug |0.5 |Example.Multiple Suites.Secondary Suite |
| Yet An Another Warning |0.0 |Example.Multiple Suites.Ternary Suite |
| First Test |0.2 |Example.Single Suite.Initial Suite |
| Issue a Warning |0.0 |Example.Single Suite.Initial Suite |

# ❌ Failing tests

| Testcase | Message | Duration (sec) | Suite |
|:---------|:--------|---------------:|:------|
| This will just be for debugging purposes |This Suite will completely fail with assertation: True !=<br/>False |0.0 |Example.Multiple Suites.Ternary Suite |
| And so is this |This Suite will completely fail |2.0 |Example.Multiple Suites.Ternary Suite |
| Second Test |For the heck of it, lets mark this case as failure |0.3 |Example.Single Suite.Initial Suite |
| Forth Test With Very Long Message |TimeoutError: page.waitForNavigation: Timeout 10000ms<br/>exceeded.<br/>=========================== logs<br/>===========================<br/>waiting for navigation to |0.0 |Example.Single Suite.Initial Suite |

# ⏩ Skipped tests

| Testcase | Message | Duration (sec) | Suite |
|:---------|:--------|---------------:|:------|
| Third One Is Skipped |This Test Will Be Skipped |0.0 |Example.Single Suite.Initial Suite |

# ⚠ Warnings

| Test Case | Message | Suite |
|:----------|:--------|:------|
| Yet An Another Warning |Another warning, pay attention |Example.Multiple Suites.Ternary Suite |
| Issue a Warning |Warning to all rudeboys! |Example.Single Suite.Initial Suite |

