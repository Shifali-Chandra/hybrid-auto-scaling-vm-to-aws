import psutil
import time
import os

THRESHOLD = 75  # CPU usage threshold in percent

def get_instance_count():
    output = os.popen(
        "aws autoscaling describe-auto-scaling-groups "
        "--query \"AutoScalingGroups[0].Instances[?LifecycleState=='InService'].InstanceId\" "
        "--output text"
    ).read()

    if output.strip() == "":
        return 0

    return len(output.strip().split())

print("Monitoring CPU and Instance Count...\n")

while True:
    cpu = psutil.cpu_percent(interval=5)
    instances = get_instance_count()

    print(f"CPU Usage: {cpu}%")
    print(f"Instances running: {instances}\n")

    if cpu > THRESHOLD:
        print("Threshold exceeded! Triggering scaling...\n")

        os.system("python3 trigger_ec2.py")

        time.sleep(15)

        instances_after = get_instance_count()
        print(f"Instances after scaling: {instances_after}")
        break

    time.sleep(3)
