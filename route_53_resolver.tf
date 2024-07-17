/*provider "aws" {
   region = "us-east-1"
}
*/
data "aws_route53_resolver_rules" "shared_rules" {
  share_status = "SHARED_WITH_ME"
}
data "aws_vpcs" "all_vpcs"{}

locals {
  resolver_rule_ids = data.aws_route53_resolver_rules.shared_rules.resolver_rule_ids
  vpc_ids           = data.aws_vpcs.all_vpcs.ids
  rule_vpc_pairs    = toset(setproduct(local.resolver_rule_ids, local.vpc_ids))
}

resource "aws_route53_resolver_rule_association" "vpc_associations" {
  for_each = { for pair in local.rule_vpc_pairs : "${pair[0]}-${pair[1]}" => pair }
  resolver_rule_id = each.value[0]
  vpc_id           = each.value[1]
}

output "generated_combinations" {
  value = local.rule_vpc_pairs
}


