# -*- coding: utf-8 -*-

from ScoutSuite.providers.azure.configs.base import AzureBaseConfig


class NetworkConfig(AzureBaseConfig):
    targets = (
        ('network_watchers', 'Network Watchers', 'list_all', {}, False),
        ('network_security_groups', 'Network Security Group', 'list_all', {}, False),
    )

    def __init__(self, thread_config):
        self.network_watchers = {}
        self.network_watchers_count = 0

        self.network_security_groups = {}
        self.network_security_groups_count = 0

        super(NetworkConfig, self).__init__(thread_config)

    def parse_network_watchers(self, network_watcher, params):
        network_watcher_dict = {}
        network_watcher_dict['id'] = network_watcher.id
        network_watcher_dict['name'] = network_watcher.name
        network_watcher_dict['provisioning_state'] = network_watcher.provisioning_state == "Succeeded"
        network_watcher_dict['location'] = network_watcher.location
        network_watcher_dict['etag'] = network_watcher.etag

        self.network_watchers[network_watcher_dict['id']] = network_watcher_dict

    def parse_network_security_groups(self, network_security_group, params):
        network_security_group_dict = {}
        network_security_group_dict['id'] = network_security_group.id
        network_security_group_dict['name'] = network_security_group.name
        network_security_group_dict['provisioning_state'] = network_security_group.provisioning_state
        network_security_group_dict['location'] = network_security_group.location
        network_security_group_dict['resource_guid'] = network_security_group.resource_guid
        network_security_group_dict['etag'] = network_security_group.etag

        network_security_group_dict['security_rules'] = self._parse_security_rules(network_security_group)

        self.network_security_groups[network_security_group_dict['id']] = network_security_group_dict

    def _parse_security_rules(self, network_security_group):
        security_rules = {}
        for sr in network_security_group.security_rules:
            security_rule_dict = {}
            security_rule_dict['id'] = sr.id
            security_rule_dict['name'] = sr.name
            security_rule_dict['allow'] = sr.access == "Allow"
            security_rule_dict['priority'] = sr.priority
            security_rule_dict['description'] = sr.description
            security_rule_dict['provisioning_state'] = sr.provisioning_state

            security_rule_dict['protocol'] = sr.protocol
            security_rule_dict['direction'] = sr.direction
            security_rule_dict['source_address_prefix'] = sr.source_address_prefix
            security_rule_dict['source_ports'] = self._parse_ports(sr.source_port_range, sr.source_port_ranges)
            security_rule_dict['destination_address_prefix '] = sr.destination_address_prefix
            security_rule_dict['destination_ports'] = self._parse_ports(sr.destination_port_range,
                                                                        sr.destination_port_ranges)

            security_rule_dict['etag'] = sr.etag

            security_rules[security_rule_dict['id']] = security_rule_dict

        return security_rules

    @staticmethod
    def _parse_ports(port_range, port_ranges):
        ports = set()
        port_ranges = port_ranges if port_ranges else []
        if port_range:
            port_ranges.append(port_range)
        for pr in port_ranges:
            if pr == "*":
                for p in range(0, 65535 + 1):
                    ports.add(p)
                break
            elif "-" in pr:
                lower, upper = pr.split("-")
                for p in range(int(lower), int(upper) + 1):
                    ports.add(p)
            else:
                ports.add(int(pr))
        return list(ports)