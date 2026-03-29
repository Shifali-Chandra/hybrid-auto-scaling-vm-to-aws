# Hybrid Auto-Scaling Assignment

## 1. Project Overview

This project demonstrates the implementation of a hybrid cloud auto-scaling system where a local virtual machine monitors its CPU utilization and dynamically triggers scaling of cloud capacity in AWS when the usage exceeds a defined threshold.

The system simulates a high-availability scenario where a sample application is assumed to be available on both the local VM and a baseline cloud instance. The local VM handles the primary workload, while the cloud environment maintains standby capacity. When CPU utilization on the local VM exceeds the defined threshold, additional cloud instances are provisioned using the Auto Scaling Group to handle increased demand. This demonstrates how cloud resources can be dynamically scaled to support high availability and workload expansion.

The project implements:

- Local Virtual Machine setup using VirtualBox running Ubuntu Linux
- CPU monitoring using a Python script with the psutil library as monitor.py
- Threshold-based trigger mechanism to detect high resource usage as trigger_ec2.py
- Integration with AWS Auto Scaling Group using AWS CLI
- Automated provisioning of EC2 instances based on local CPU usage %

---

## 2. Local VM Setup

The local environment was set up using VirtualBox to simulate an on-premise infrastructure. The virtual machine from Assignment 1 was reused for this project.

### Step 1: Virtual Machine Configuration

The existing VM `CampusEats-VM1` from Assignment 1 was reused with the following configuration:

- **Name**: CampusEats-VM1
- **Platform**: VirtualBox
- **OS**: Ubuntu Linux
- **RAM**: 2048 MB
- **CPU**: 1 core
- **Hard Disk**: 20 GB

### Step 2: Network Configuration

In Assignment 1, the VM network adapter was set to **Host-Only Adapter** mode to allow local VM-to-VM communication. For this assignment, the adapter was reconfigured to **NAT mode** to allow the virtual machine to communicate with the internet and reach AWS cloud services.

### Step 3: Application Setup

Python3 was installed and the `psutil` library was added for CPU monitoring:

```bash
pip install psutil
```

The AWS CLI was installed and configured with IAM credentials - Access key and secret key:

```bash
aws configure
```

Connectivity to AWS was verified using:

```bash
aws ec2 describe-instances
```

---

## 3. Monitoring Implementation

A CPU monitoring system was implemented using Python and the psutil library.

### Script: monitor.py

The script continuously monitors CPU usage every 5 seconds and compares it against the defined threshold.

The exact script used is as following:

```python
import psutil
import subprocess
import time

THRESHOLD = 75

print("Monitoring CPU and Instance Count...")

while True:
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=5)
    
    # Get number of running EC2 instances
    result = subprocess.run(
        ['aws', 'autoscaling', 'describe-auto-scaling-groups', 
         '--query', 'AutoScalingGroups[0].Instances[?LifecycleState==\'InService\'].InstanceId', 
         '--output', 'text'],
        capture_output=True, text=True
    )
    instances = result.stdout.strip().split()
    instance_count = len(instances)
    
    print(f"\nCPU Usage: {cpu_usage}%")
    print(f"Instances running: {instance_count}")
    
    # Check if CPU usage exceeds threshold
    if cpu_usage > THRESHOLD:
        print("Threshold exceeded! Triggering scaling...")
        
        # Trigger scaling
        subprocess.run(['python3', 'trigger_ec2.py'])
        
        # Wait for scaling to complete
        time.sleep(15)
        
        # Get updated instance count
        result = subprocess.run(
            ['aws', 'autoscaling', 'describe-auto-scaling-groups', 
             '--query', 'AutoScalingGroups[0].Instances[?LifecycleState==\'InService\'].InstanceId', 
             '--output', 'text'],
            capture_output=True, text=True
        )
        instances = result.stdout.strip().split()
        instance_count = len(instances)
        
        print(f"Instances after scaling: {instance_count}")
    
    time.sleep(5)
```

Few important points about the script:

- The script runs in an infinite loop until scaling is triggered, continuously monitoring CPU usage and instance count
- The script uses the `psutil` library to monitor CPU usage
- The script uses the AWS CLI to monitor instance count
- The script uses the `subprocess` module to execute the AWS CLI command
- The script uses the `time` module to sleep for 5 seconds between each polling cycle
- The current number of running EC2 instances is also fetched using the AWS CLI on each polling cycle
- Both values of CPU usage and instance count are printed to the terminal in real time for monitoring

---

## 4. Threshold-Based Trigger Mechanism

A threshold-based logic was implemented to trigger cloud scaling when CPU usage exceeds 75%.

### Threshold Definition

```python
THRESHOLD = 75
```

When CPU usage exceeds the threshold:
- The scaling script `trigger_ec2.py` is executed automatically
- The script waits 15 seconds for the instance to launch
- The updated instance count is fetched and printed to confirm scaling

### The `trigger_ec2.py` Script

Here is the complete code for the trigger script:

```python
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
```

Few important points about the script:

- The script uses the `os.system()` function to execute the AWS CLI command directly from Python
- The AWS CLI command `set-desired-capacity` instructs the Auto Scaling Group to increase the number of running instances to 2
- The Auto Scaling Group name `AutoScalingGroup` must match the name configured in the AWS Console
- The script checks the return code of the command — 0 indicates success, any non-zero value indicates failure
- A success or failure message is printed to the terminal based on the return code
- This implementation simulates a small-scale hybrid auto-scaling setup. At larger scale, the trigger mechanism can be replaced with AWS Auto Scaling Policies and CloudWatch Alarms for more dynamic and automated scaling behaviour

---

## 5. AWS Integration Setup

The local VM was integrated with AWS using the AWS CLI and an IAM user with programmatic access.

### Step 1: IAM Configuration

An IAM user was created with programmatic access and the following permissions assigned:

- `autoscaling:SetDesiredCapacity`
- `autoscaling:DescribeAutoScalingGroups`
- `ec2:DescribeInstances`

### Step 2: AWS CLI Configuration

The AWS CLI was configured on the local VM using the IAM access keys:

```bash
aws configure
```

This stores the credentials locally and allows the Python scripts to communicate with AWS services.

---

## 6. AWS Infrastructure Setup (Reused from Assignment 2)

The AWS cloud infrastructure from Assignment 2 was reused for this project without modification. This includes the EC2 Launch Template, Auto Scaling Group, IAM Role, and Security Group — all originally configured in Assignment 2. The local VM in this assignment integrates directly with this existing infrastructure to trigger scaling via the AWS CLI.

Note: Assignment 2 had a CPU-based **Target Tracking Scaling Policy** configured on the Auto Scaling Group. That policy is not used in this assignment. Instead, scaling is triggered manually and programmatically from the local VM using the AWS CLI command in `trigger_ec2.py`.

### Components Used

- EC2 (Elastic Compute Cloud)
- Auto Scaling Group
- Launch Template
- IAM Role
- Security Group

### Step 1: IAM Role

An IAM Role named `EC2-AutoScaling-Role` is attached to EC2 instances to allow secure access to AWS services.

- **Trusted Entity**: EC2
- **Policy Attached**: AmazonSSMManagedInstanceCore

### Step 2: Security Group

A Security Group named `AutoScaling-SG` is configured as a firewall for the EC2 instances.

**Inbound Rules:**
- HTTP (Port 80) — open to all (0.0.0.0/0) for public web access
- SSH (Port 22) — restricted to My IP only for admin access

**Outbound Rules:**
- All traffic allowed (kept as default)

### Step 3: Launch Template

The **Launch Template** from Assignment 2 was used to allow automated and consistent instance provisioning through the Auto Scaling Group.

Configuration:
- **Origin**: Created in Assignment 2, reused without changes
- **AMI**: Amazon Linux 2 (64-bit x86)
- **Instance Type**: t3.micro
- **IAM Role**: EC2-AutoScaling-Role
- **Security Group**: AutoScaling-SG
- **User Data**: Bootstrap script (given below)

A bootstrap script was attached to the Launch Template. It runs automatically on every new instance creation.

```bash
#!/bin/bash
# Install and start Apache
yum update -y
yum install httpd -y
systemctl start httpd
systemctl enable httpd
# Display hostname to verify auto scaling
echo "Hello from Auto Scaling - Hostname: $(hostname)" > /var/www/html/index.html
```

This script installs Apache Web Server and displays the instance hostname on a webpage to verify that new instances are correctly provisioned during auto scaling.

### Step 4: Auto Scaling Group

An **Auto Scaling Group** named `AutoScalingGroup` was created using the Launch Template.

Configuration:
- **Minimum Capacity**: 1
- **Desired Capacity**: 1
- **Maximum Capacity**: 2
- **Multi-AZ Deployment**: Enabled

This ensures at least one instance is always running and the system can scale up to a maximum of two instances when triggered. In this assignment, the desired capacity is increased from 1 to 2 programmatically by `trigger_ec2.py` using the AWS CLI, instead of relying on CloudWatch-based auto scaling policies.

---

## 7. Architecture Design

The following diagram illustrates the complete system architecture:

![Hybrid Auto-Scaling Architecture](./architecture.png)

### Architecture Overview

The architecture is organized into three primary layers:

1. **Local VM (On-Premise Layer):** Running on VirtualBox, this layer hosts the application workload and executes the `monitor.py` script. It continuously monitors CPU utilization using the `psutil` library and applies threshold-based logic in real time. To simulate increased workload, a PowerShell terminal is used to SSH into the local VM and run the `stress --cpu 2` command, which artificially raises CPU usage to trigger the scaling threshold.

2. **Monitoring and Trigger Layer:** This layer acts as the bridge between the local environment and the cloud. It performs a CPU threshold check and, when usage exceeds 75%, the monitoring script invokes `trigger_ec2.py`, which issues a scaling command to AWS through the AWS CLI.

3. **AWS Cloud Layer:** Upon receiving the scale trigger, the Auto Scaling Group increases its desired capacity and provisions additional EC2 instances. These instances provide extra compute capacity to support the increased workload demand.

---

## 8. Testing and Validation

The system was tested using a simulated CPU workload on the local VM.

### Testing Steps

- Monitoring script `monitor.py` was started on the local VM
- CPU load was generated using the Linux `stress` tool to push utilization above 75%
- The monitoring script detected the threshold breach and automatically executed `trigger_ec2.py`
- The AWS Auto Scaling Group increased desired capacity from 1 to 2
- CPU usage was increased above 75%, and the instance count was simultaneously updated from 1 to 2, confirming the end-to-end scaling behaviour

### Observed Output

```
Monitoring CPU and Instance Count...

CPU Usage: 100%
Instances running: 1

Threshold exceeded! Triggering scaling...

Scaling AWS Auto Scaling Group...
Scaling command executed successfully!

Instances after scaling: 2
```

This confirms that the system works end-to-end as expected, from CPU spike detection on the local VM to automated EC2 instance provisioning on AWS.

---

## 9. Conclusion

This assignment successfully shows the following:

- Monitoring of local VM CPU usage using Python and psutil
- Threshold-based automated trigger mechanism to detect resource overload
- Integration between local VM and AWS instances - A hybrid setup
- Dynamic provisioning of EC2 instances using AWS Auto Scaling Group

The system effectively demonstrates a real-world hybrid cloud bursting scenario, where a local VM communicates with AWS to dynamically provision additional EC2 instances in response to rising CPU demand, bridging on-premise infrastructure with scalable cloud capacity.
