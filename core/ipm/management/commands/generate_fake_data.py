import random
import ipaddress
from faker import Faker
from ipm.models import VlanModel, IPPoolModel  # adjust app name if needed

fake = Faker()

def create_fake_vlan():
    vlan = VlanModel.objects.create(
        name=fake.word().capitalize() + " VLAN",
        vlan_id=random.randint(1, 2048),
        description=fake.sentence(),
        category=random.choice([1, 2, 3]),  # 1=Private, 2=Public, 3=Other
        vpn_name=fake.domain_word(),
        is_visible_to_users=random.choice([True, False]),
        status=random.choice([True, False])
    )
    return vlan

def create_fake_ip_pool(vlan):
    # Generate a random subnet

    network = ipaddress.IPv4Network(fake.ipv4(network=True), strict=False)
    ip_list = list(network.hosts())

    start_ip = str(ip_list[10])
    end_ip = str(ip_list[200])
    gateway = str(ip_list[1])
    subnet_mask = str(network.netmask)

    IPPoolModel.objects.create(
        vlan=vlan,
        ip_range_start=start_ip,
        ip_range_end=end_ip,
        subnet_mask=subnet_mask,
        gateway=gateway,
        dns_servers=f"{ip_list[2]},{ip_list[3]}",
        description=fake.text(max_nb_chars=100),
        is_active=True
    )

# 🔁 Generate multiple entries
for _ in range(10):
    vlan = create_fake_vlan()
    create_fake_ip_pool(vlan)