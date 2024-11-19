# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DashboardDatacenter(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    ip = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'dashboard_datacenter'


class DashboardDomain(models.Model):
    uuid = models.UUIDField(db_column='UUID', primary_key=True)  # Field name made lowercase.
    id = models.IntegerField()
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    max_ram = models.IntegerField()
    current_ram = models.IntegerField()
    vcpus = models.IntegerField()
    vnc_port = models.IntegerField(blank=True, null=True)
    proxy_port = models.IntegerField(blank=True, null=True)
    ip = models.CharField(max_length=15)
    mac_address = models.CharField(db_column='mac-address', max_length=18, blank=True, null=True)  # Field renamed to remove unsuitable characters.
    node = models.ForeignKey('DashboardNode', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dashboard_domain'


class DashboardNode(models.Model):
    id = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    datacenter = models.ForeignKey(DashboardDatacenter, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dashboard_node'
