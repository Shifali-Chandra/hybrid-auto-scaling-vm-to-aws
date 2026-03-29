# Hybrid Auto-Scaling Assignment
Local VM CPU Monitoring with Automated Scaling to AWS EC2

## What This Project Does

This project monitors CPU usage on a local virtual machine (VirtualBox/Ubuntu) using a Python script. When CPU utilization exceeds 75%, the system automatically triggers AWS Auto Scaling to increase the number of running EC2 instances — simulating a real-world hybrid cloud bursting scenario where on-premise infrastructure dynamically extends to the cloud.

## Reused Infrastructure

- **Local VM** (`CampusEats-VM1`) — Originally created in Assignment 1. Network adapter reconfigured from Host-Only to NAT mode for AWS access.
- **AWS Infrastructure** — Auto Scaling Group, Launch Template, IAM Role, and Security Group all reused from Assignment 2 without modification. The Assignment 2 CPU-based Target Tracking Scaling Policy is not used here; scaling is triggered programmatically from the local VM instead.

## AWS Resources

| Resource | Name / Details |
|---|---|
| Auto Scaling Group | `AutoScalingGroup` — Min: 1, Desired: 1, Max: 2 |
| Launch Template | From Assignment 2 — Amazon Linux 2, t3.micro |
| IAM Role | `EC2-AutoScaling-Role` — Attached to EC2 instances (AmazonSSMManagedInstanceCore) |
| IAM User | Programmatic access on local VM — `autoscaling:SetDesiredCapacity`, `autoscaling:DescribeAutoScalingGroups`, `ec2:DescribeInstances` |
| Security Group | `AutoScaling-SG` — HTTP (80) open, SSH (22) restricted to My IP |

## Local VM Setup

- **Platform** — VirtualBox running Ubuntu Linux (reused from Assignment 1)
- **Resources** — 2 GB RAM, 1 CPU, 20 GB Disk
- **Network** — NAT adapter (reconfigured from Host-Only) for internet and AWS access
- **Dependencies** — `psutil` for CPU monitoring, AWS CLI configured with IAM access keys

## How It Works

```
Local VM (monitor.py)
  → polls CPU every 5 seconds using psutil
  → CPU > 75% detected
  → calls trigger_ec2.py
  → AWS CLI: set-desired-capacity = 2
  → Auto Scaling Group launches new EC2 instance
  → instance count confirmed: 1 → 2
```

## Files

| File | Purpose |
|---|---|
| `monitor.py` | Continuously monitors CPU usage and triggers scaling when threshold is exceeded |
| `trigger_ec2.py` | Executes the AWS CLI command to increase Auto Scaling Group desired capacity |
| `DOCUMENTATION_REPORT.md` | Full step-by-step implementation details |
| `architecture.png` | System architecture diagram |
