import os

print("Scaling AWS Auto Scaling Group...")

result = os.system(
    "aws autoscaling set-desired-capacity "
    "--auto-scaling-group-name AutoScalingGroup "
    "--desired-capacity 2"
)

if result == 0:
    print("Scaling command executed successfully!")
else:
    print("Scaling command failed!")
