To configure Ansible to use a PEM file for SSH connections to run playbooks on an EC2 instance, you need to specify the path to your PEM file in either your Ansible inventory file (hosts file) or directly in your playbook. Here's how to do it:

### Option 1: Using the Ansible Inventory File

Your Ansible inventory file (`hosts` or `inventory.ini`) defines the groups of hosts (in this case, your EC2 instances) that your playbooks will run against. You can specify SSH connection parameters, including the path to your PEM file, in this inventory file.

1. **Create or Edit Your Inventory File**: Open your inventory file in a text editor. If you don't already have one, create a file named `hosts` or `inventory.ini`.

2. **Add Your EC2 Instance and Specify the PEM File**:
    ```ini
    [ec2_instances]
    your_ec2_public_dns_or_ip ansible_user=ec2-user ansible_ssh_private_key_file=/path/to/your-key-pair.pem
    ```
    - Replace `your_ec2_public_dns_or_ip` with the public DNS name or IP address of your EC2 instance.
    - Replace `ec2-user` with the appropriate username for your EC2 instance's OS (e.g., `ubuntu` for Ubuntu instances).
    - Replace `/path/to/your-key-pair.pem` with the actual path to your PEM file.

3. **Run Your Playbook**:
    ```bash
    ansible-playbook -i hosts your_playbook.yml
    ```

### Option 2: Specifying the PEM File Directly in Your Playbook

You can also specify the SSH connection details directly in your playbook. This approach is useful if you're running tasks on a small number of instances or if the connection details vary between playbooks.

1. **Edit Your Playbook**: Open your playbook in a text editor.

2. **Add Connection Variables**:
    ```yaml
    ---
    - name: Run tasks on EC2 instance
      hosts: all
      vars:
        ansible_user: ec2-user
        ansible_ssh_private_key_file: /path/to/your-key-pair.pem
      tasks:
        - name: Example task
          command: echo "Hello, World!"
    ```

    - Set `ansible_user` to the username for your EC2 instance.
    - Set `ansible_ssh_private_key_file` to the path to your PEM file.

3. **Run Your Playbook**, specifying your EC2 instance's public DNS or IP address directly in the command:
    ```bash
    ansible-playbook your_playbook.yml -i 'your_ec2_public_dns_or_ip,'
    ```
    Note the comma after the IP address or DNS name, which Ansible requires to interpret the string as a list of hosts.

### Additional Tips

- **Permissions**: Ensure your PEM file's permissions are set correctly (readable by the user running Ansible, typically `400` or `600`).
- **Ansible Configuration File**: You can also specify default connection variables in the Ansible configuration file (`ansible.cfg`) for more global settings.
- **Security Groups**: Verify that the security group associated with your EC2 instance allows inbound SSH connections (port 22) from your IP address.

By configuring Ansible with the path to your PEM file, you enable Ansible to use SSH for connecting to your EC2 instance and running your automation tasks.