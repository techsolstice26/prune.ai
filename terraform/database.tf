
resource "aws_db_instance" "timescaledb" {
  identifier           = "cloudscope-timescaledb"
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t4g.micro" # Free Tier Eligible
  allocated_storage    = 20
  storage_type         = "gp2"
  username             = "postgres"
  password             = var.db_password
  skip_final_snapshot  = true
  publicly_accessible  = true
  
  vpc_security_group_ids = [aws_security_group.db_sg.id]
}

resource "aws_security_group" "db_sg" {
  name        = "timescaledb_sg"
  description = "Allow inbound PostgreSQL traffic"

  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
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
