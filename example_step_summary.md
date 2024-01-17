
---
# Totals

| Passed ✅ | Failed ❌ | Skipped ⏩ | Total | Passrate % | Duration (sec) |
|:--------:|:--------:|:---------:|:-----:|-----------:|---------------:|
| 3 | 3 | 1 | 7 | 42.86 | 4.1 |

# ✅ Passing tests

| Testcase | Duration (sec) | Suite |
|:---------|---------------:|:------|
| Third Test With maybe longer name | 1.0 | Example.Multiple Suites.Secondary Suite |
| Fourth suite and we still want something more to debug | 0.5 | Example.Multiple Suites.Secondary Suite |
| First Test | 0.2 | Example.Single Suite.Initial Suite |

# ❌ Failing tests

| Testcase | Message | Duration (sec) | Suite |
|:---------|:--------|---------------:|:------|
| This will just be for debugging purposes | This Suite will completely fail with assertation: True != False | 0.0 | Example.Multiple Suites.Ternary Suite |
| And so is this | This Suite will completely fail | 2.0 | Example.Multiple Suites.Ternary Suite |
| Second Test | For the heck of it, lets mark this case as failure | 0.3 | Example.Single Suite.Initial Suite |

# ⏩ Skipped tests

| Testcase | Message | Duration (sec) | Suite |
|:---------|:--------|---------------:|:------|
| Third One Is Skipped | This Test Will Be Skipped | 0.0 | Example.Single Suite.Initial Suite |

