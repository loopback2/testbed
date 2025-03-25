from yaspin import yaspin
import time

# Choose a cool spinner from https://github.com/pavdmyt/yaspin#spinners
with yaspin(text="Waiting for SSH...", color="cyan", spinner="dots12") as spinner:
    for _ in range(30):  # Simulate waiting (30 * 0.2 = 6 seconds)
        time.sleep(0.2)
        spinner.text = "Still waiting for SSH..."

    # Now simulate success
    spinner.ok("✅")
    print("SSH is now reachable.")