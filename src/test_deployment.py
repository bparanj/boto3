from src.ec2.vpc import VPC
from src.client_locator import EC2Client
from src.ec2.ec2 import EC2
import os

def main():
    # Create a VPC
    ec2_client = EC2Client().get_client()
    vpc = VPC(ec2_client)
    vpc_response = vpc.create_vpc()

    print('VPC created:' + str(vpc_response))

    #     Add name tag to VPC
    vpc_name = 'Boto3-VPC'
    vpc_id = vpc_response['Vpc']['VpcId']
    vpc.add_name_tag(vpc_id, vpc_name)

    print('Added ' + vpc_name + ' to ' + vpc_id)

    #     Create an IGW
    gateway_response = vpc.create_internet_gateway()
    igw_id = gateway_response['InternetGateway']['InternetGatewayId']

    vpc.attach_igw_to_vpc(vpc_id, igw_id)

    # Create a public subnet
    public_subnet_response = vpc.create_subnet(vpc_id, cidr_block='10.0.1.0/24')
    public_subnet_id = public_subnet_response['Subnet']['SubnetId']

    print('Subnet created for vpc:' + vpc_id + ':' + str(public_subnet_response))

    # Add name tag to Public Subnet
    vpc.add_name_tag(public_subnet_id, 'Boto3-Public-Subnet')

    # Create a public route table
    public_route_table_response = vpc.create_public_route_table(vpc_id)

    rtb_id = public_route_table_response['RouteTable']['RouteTableId']

    # Adding the IGW to public route table
    vpc.create_igw_route_to_public_route_table(rtb_id, igw_id)

    # Associate Public Subnet with route table
    vpc.associate_subnet_with_route_table(public_subnet_id, rtb_id)

    # Allow auto assign public IP addresses for subnet
    vpc.allow_auto_assign_ip_addresses_for_subnet(public_subnet_id)

    # Create a private subnet
    private_subnet_response = vpc.create_subnet(vpc_id, '10.0.2.0/24')
    private_subnet_id = private_subnet_response['Subnet']['SubnetId']

    print('Created private subnet ' + private_subnet_id + ' for VPC ' + vpc_id)

    # Add name tag to private subnet
    vpc.add_name_tag(private_subnet_id, 'Boto3-Private-Subnet')

    # EC2 instances
    ec2 = EC2(ec2_client)

    # Create a key pair
    key_pair_name = "Boto3-KeyPair"
    key_pair_response = ec2.create_key_pair(key_pair_name)

    print('Created key pair ' + key_pair_name + ' : ' + str(key_pair_response))

    # Extract the KeyMaterial, which is the private key
    key_material = key_pair_response['KeyMaterial']

    # Define the file name for the private key
    key_file_name = f"{key_pair_name}.pem"

    # Save the private key to a .pem file
    with open(key_file_name, 'w') as key_file:
        key_file.write(key_material)

    # Set the file's permissions to read-only for the file owner
    os.chmod(key_file_name, 0o400)

    print(f"Key pair saved to {key_file_name} with read-only permissions for the file owner.")

    # Create a Security Group
    public_security_group_name = 'Boto3-Public-SG'
    public_security_group_description = 'Public Security Group for Public Subnet Internet Access'
    public_security_group_response = ec2.create_security_group(public_security_group_name,
                                                               public_security_group_description,
                                                               vpc_id)
    public_security_group_id = public_security_group_response['GroupId']

    # Add public access to security group
    ec2.add_inbound_rule_to_sg(public_security_group_id)

    print('Added public access rule to security group: ' + public_security_group_name)

    user_data = """#!/bin/bash
                sudo apt-get update -y
                sudo apt-get install apache2 -y
                sudo systemctl start apache2
                sudo systemctl enable apache2
                echo "<html><body><h1>Hello Boto3 using Python</h1></body></html>" > /var/www/html/index.html"""

    ami_id = 'ami-0e21465cede02fd1e'

    # Launch a public EC2 instance
    ec2.launch_ec2_instance(ami_id,
                            key_pair_name,
                            1,
                            1,
                            public_security_group_id,
                            public_subnet_id,
                            user_data)

    print('Launched EC2 instance using AMI ami-0e21465cede02fd1e')

    # Adding another security group for private EC2 instance
    private_security_group_name = 'Boto3-Private-SG'
    private_security_group_description = 'Private security group for private subnet'
    private_security_group_response = ec2.create_security_group(private_security_group_name,
                                                                private_security_group_description, vpc_id)

    private_security_group_id = private_security_group_response['GroupId']

    # Add rule to private security group
    ec2.add_inbound_rule_to_sg(private_security_group_id)

    # Launch a private EC2
    ec2.launch_ec2_instance(ami_id, key_pair_name, 1, 1, private_security_group_id, private_subnet_id, """""""")


if __name__ == '__main__':
    main()
