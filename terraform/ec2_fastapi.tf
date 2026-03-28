data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"] # Canonical
}

resource "aws_security_group" "fastapi_sg" {
  name        = "fastapi_sg"
  description = "Allow port 8000 for FastAPI WebSockets"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "fastapi_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  key_name      = "CloudScope-Key"
  iam_instance_profile = aws_iam_instance_profile.fastapi_ec2_profile.name

  vpc_security_group_ids = [aws_security_group.fastapi_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y python3-pip python3-venv
              EOF

  tags = {
    Name = "CloudScope-Dashboard-Server"
  }
}

# SECOND INSTANCE: THE "TARGET" FOR REMEDIATION DEMO
resource "aws_instance" "target_instance" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  key_name      = "CloudScope-Key"

  vpc_security_group_ids = [aws_security_group.fastapi_sg.id]

  tags = {
    Name = "CloudScope-Anomaly-Target"
  }
}

output "target_id" {
  value = aws_instance.target_instance.id
}
