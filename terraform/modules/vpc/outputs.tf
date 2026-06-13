output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "alb_sg_id" {
  value = aws_security_group.alb_sg.id
}

output "ecs_sg_id" {
  value = aws_security_group.ecs_sg.id
}

output "private_route_table_id" {
  description = "Private route table ID (Lambda will manage NAT GW route here)"
  value       = aws_route_table.private.id
}

output "first_public_subnet_id" {
  description = "First public subnet ID (where NAT GW lives)"
  value       = aws_subnet.public[0].id
}

output "nat_eip_allocation_id" {
  description = "Elastic IP allocation ID used by NAT Gateway"
  value       = aws_eip.nat.id
}

output "nat_gateway_id" {
  description = "Current NAT Gateway ID"
  value       = aws_nat_gateway.nat.id
}
