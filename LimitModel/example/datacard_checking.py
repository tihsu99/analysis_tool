import CombineHarvester.CombineTools.ch as ch
import os

# Path to the datacard (update with your actual path)
datacard_path = "/eos/user/t/tihsu/bHplus/full_run2_v7_w_reco_mass/Limit_study_DNN_v8_ABCD_likelihood/datacards_g2HDM_separate/run2/CGToBHpm_a_500_rtt06_rtc04/CGToBHpm_a_500_rtt06_rtc04_run2_C_C.txt"

# Initialize CombineHarvester instance
cb = ch.CombineHarvester()

# Parse the datacard to load its components
cb.ParseDatacard(datacard_path)

# Print basic information about the datacard
print("Datacard loaded successfully.")
print("Processes in the datacard:")
for proc in cb.processes():
    print(f" - {proc}")

# Check categories and their assigned processes
print("\nCategories and associated processes:")
for category in cb.categories():
    processes_in_category = cb.GetProcessesForCategory(category)
    print(f"Category: {category}")
    if processes_in_category:
        for proc in processes_in_category:
            print(f"  - {proc}")
    else:
        print("  - No processes assigned.")

# Check systematics and their assignments to processes
print("\nSystematics and their processes:")
for syst in cb.systematics():
    processes_for_syst = cb.GetProcessesForSystematic(syst)
    print(f"Systematic: {syst}")
    if processes_for_syst:
        for proc in processes_for_syst:
            print(f"  - {proc}")
    else:
        print("  - No processes affected.")

# Optionally, you can print the full content of the datacard
print("\nDatacard content:")
cb.PrintDatacard()

# Additional checks can be added as necessary, such as verifying missing components
print("\nCheck for unused processes:")
for proc in cb.processes():
    used_in_any_category = any(cb.GetProcessesForCategory(cat) for cat in cb.categories())
    if not used_in_any_category:
        print(f"Process {proc} is unused.")

print("\nDebugging complete.")

