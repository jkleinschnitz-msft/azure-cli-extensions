# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest, live_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
import time


def reset_softdelete_base_state(test):
    # Ensure backup instance is deleted from the secondary vault. If instance is already deleted, it will return instantly. As soft delete is disabled
    # on this vault, it should not show up in the soft-deleted items there
    test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName2}" --yes')
    test.cmd('az dataprotection backup-instance deleted-backup-instance list -g "{rg}" --vault-name "{vaultName}"', checks=[
        test.check('length([])', 0)
    ])

    # Ensure that backup instance is protected in the primary soft delete vault
    test.cmd('az dataprotection backup-instance deleted-backup-instance undelete -g "{rg}" --vault-name "{softDeleteVault}" --name "{backupInstanceName1}"')
    test.cmd('az dataprotection backup-instance resume-protection -g "{rg}" --vault-name "{softDeleteVault}" --name "{backupInstanceName1}"')
    test.cmd('az dataprotection backup-instance show -g "{rg}" --vault-name "{softDeleteVault}" --name "{backupInstanceName1}"', checks=[
        test.check('properties.protectionStatus.status', "ProtectionConfigured")
    ])


# Uses a persistent vault and persistent DSes
class BackupInstanceOperationsScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'rg': 'clitest-dpp-rg',
            'vaultName': 'clitest-bkp-vault-persistent-bi-donotdelete',
            'softDeleteVault': 'clitest-bkp-vault-sd1-donotdelete',
            'uamiVault': 'clitest-bkp-vault-uami-donotdelete',
        })

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_update_protection(test):
        test.kwargs.update({
            'backupInstanceName': 'clitest-disk-persistent-bi-donotdelete-clitest-disk-persistent-bi-donotdelete-e33c80ba-0bf8-11ee-aaa6-002b670b472e'
        })
        test.addCleanup(test.cmd, 'az dataprotection backup-instance resume-protection -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')

        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 600 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')

        test.cmd('az dataprotection backup-instance stop-protection -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')
        test.cmd('az dataprotection backup-instance show -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.currentProtectionState', 'ProtectionStopped')
        ])

        test.cmd('az dataprotection backup-instance resume-protection -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')
        test.cmd('az dataprotection backup-instance show -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.currentProtectionState', 'ProtectionConfigured')
        ])

        test.cmd('az dataprotection backup-instance suspend-backup -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"')
        test.cmd('az dataprotection backup-instance show -n "{backupInstanceName}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('properties.currentProtectionState', 'BackupsSuspended')
        ])

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_update_policy(test):
        test.kwargs.update({
            'backupInstanceName': 'clitestsabidonotdelete-clitestsabidonotdelete-887c3538-0bfc-11ee-acd3-002b670b472e',
            'policyName': 'blobpolicy',
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-persistent-bi-donotdelete/backupPolicies/blobpolicy',
            'altPolicyName': 'altblobpolicy',
            'altPolicyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-persistent-bi-donotdelete/backupPolicies/altblobpolicy'
        })
        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 300 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')

        test.cmd('az dataprotection backup-instance update-policy -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --policy-id "{altPolicyId}"', checks=[
            test.check("contains(properties.policyInfo.policyId, '/{altPolicyName}')", True)
        ])
        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 300 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')

        test.cmd('az dataprotection backup-instance update-policy -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --policy-id "{policyId}"', checks=[
            test.check("contains(properties.policyInfo.policyId, '/{policyName}')", True)
        ])
        test.cmd('az dataprotection backup-instance wait -g "{rg}" --vault-name "{vaultName}" --backup-instance-name "{backupInstanceName}" --timeout 300 '
                 '--custom "properties.currentProtectionState==\'ProtectionConfigured\'"')

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_list_from_resource_graph(test):
        test.kwargs.update({
            'dataSourceType': 'AzureDisk',
            'dataSourceId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-persistent-bi-donotdelete',
            'backupInstanceName': 'clitest-disk-persistent-bi-donotdelete-clitest-disk-persistent-bi-donotdelete-e33c80ba-0bf8-11ee-aaa6-002b670b472e'
        })
        test.cmd('az dataprotection backup-instance list-from-resourcegraph --datasource-type "{dataSourceType}" --datasource-id "{dataSourceId}"', checks=[
            test.greater_than('length([])', 0),
            test.exists("[?name == '{backupInstanceName}']")
        ])

    @AllowLargeResponse()
    def test_dataprotection_backup_vault_list_from_resource_graph(test):
        test.kwargs.update({
            'vaultId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-persistent-bi-donotdelete',
            'vaultName': 'clitest-bkp-vault-persistent-bi-donotdelete'
        })
        test.cmd('az dataprotection backup-vault list-from-resourcegraph --vault-id "{vaultId}"', checks=[
            test.greater_than('length([])', 0),
            test.exists("[?name == '{vaultName}']")
        ])

    @AllowLargeResponse()
    @live_only()
    def test_dataprotection_backup_instance_uami_create_update(test):
        test.kwargs.update({
            'diskname': 'clitest-dpp-disk-uami-donotdelete',
            'diskId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-dpp-disk-uami-donotdelete',
            'targetDiskId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-dpp-disk-uami-target',
            'datasourceType': 'AzureDisk',
            'policyId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-uami-donotdelete/backupPolicies/clitest-dpp-uami-disk-policy',
            'backupInstanceName': 'clitest-dpp-disk-uami-donotdelete-clitest-dpp-disk-uami-donotdelete-32d2e1ea-1062-11f0-8673-cc15311bf11f',
            'uamiUrl': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/dppcliuamiccy',
        })

        test.addCleanup(test.cmd, 'az dataprotection backup-instance delete -g "{rg}" --vault-name "{uamiVault}" --backup-instance-name "{backupInstanceName}" --yes --no-wait')
        ########## PRE-TEST-VALIDATIONS ##########
        # Ensure backup-instance deletion from prev run, just in case. If instance is already deleted, it will return instantly.
        test.cmd('az dataprotection backup-vault update '
                 '-g "{rg}" -v "{uamiVault}" '
                 '--type "SystemAssigned,UserAssigned" ')
        test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{uamiVault}" --backup-instance-name "{backupInstanceName}" --yes')

        # Set Backup vault to User-Assigned only. It needs to have the same Managed Identity as we will be associating with the BI.
        test.cmd('az dataprotection backup-vault update '
                 '-g "{rg}" -v "{uamiVault}" '
                 '--type "UserAssigned" '
                 '--uami {{"{uamiUrl}":{{}}}} ',
                 checks=[
                    test.check('identity.type', 'UserAssigned')
                 ])
        
        ########## CORE TEST ##########
        # Backup Instance initialization
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize '
                                        '--datasource-id "{diskId}" '
                                        '--datasource-location "{location}" '
                                        '--datasource-type "{datasourceType}" '
                                        '--policy-id "{policyId}" '
                                        '--uami "{uamiUrl}" ', checks=[
                                            test.exists("properties.identity_details")
                                        ]).get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['backupInstanceName']
        test.kwargs.update({
            "backupInstance": backup_instance_json,
        })

        # Set permissions for Backup
        # Only run this step in live mode, if the operation is failing due to a permissions issue. Comment otherwise.
        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" -v "{uamiVault}" --datasource-type "{datasourceType}" --operation "Backup" '
                 '--permissions-scope "Resource" --backup-instance "{backupInstance}" --uami "{uamiUrl}" --yes ')

        # Validate the backup
        test.cmd('az dataprotection backup-instance validate-for-backup '
                 '-g "{rg}" -v "{uamiVault}" '
                 '--backup-instance "{backupInstance}" ')

        # Create the backup Instance
        test.cmd('az dataprotection backup-instance create '
                 '-g "{rg}" -v "{uamiVault}" '
                 '--backup-instance "{backupInstance}" ')

        # Update the vault to System+UserAssigned
        backup_vault = test.cmd('az dataprotection backup-vault update '
                                '-g "{rg}" -v "{uamiVault}" '
                               '--type "SystemAssigned,UserAssigned" ',
                                checks=[
                                    test.check('identity.type', 'SystemAssigned,UserAssigned')
                                ]).get_output_in_json()
        # Fix for 'Cannot find user or service principal in graph database' error. Confirming sp is created for the backup vault.
        sp_list = []
        while backup_vault['identity']['principalId'] not in sp_list:
            sp_list = test.cmd('az ad sp list --display-name "{vaultName}" --query [].id').get_output_in_json()
            time.sleep(10)

        # Set permissions for System Assigned Identity
        # Only run this step in live mode, if the operation is failing due to a permissions issue. Comment otherwise.
        test.cmd('az dataprotection backup-instance update-msi-permissions '
                 '-g "{rg}" -v "{uamiVault}" --datasource-type "{datasourceType}" --operation "Backup" '
                 '--permissions-scope "Resource" --backup-instance "{backupInstance}" --yes ')

        # Validate modify BI
        test.cmd('az dataprotection backup-instance validate-for-update '
                 '-g "{rg}" -v "{uamiVault}" '
                 '--backup-instance-name "{backupInstanceName}" '
                 '--use-system-identity ')

        # Modify BI
        test.cmd('az dataprotection backup-instance update '
                 '-g "{rg}" -v "{uamiVault}" '
                 '--backup-instance-name "{backupInstanceName}" '
                 '--use-system-identity ',
                 checks=[
                     test.check('properties.identityDetails.useSystemAssignedIdentity', True)
                 ])

    @AllowLargeResponse()
    def test_dataprotection_backup_instance_softdelete(test):
        test.kwargs.update({
            'diskName': 'clitest-disk-sd-donotdelete',
            'diskId': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.Compute/disks/clitest-disk-sd-donotdelete',
            'dataSourceType': "AzureDisk",
            'backupInstanceName1': "clitest-disk-sd-donotdelete-clitest-disk-sd-donotdelete-b7e6f082-b310-11eb-8f55-9cfce85d4fa1",
            'backupInstanceName2': "clitest-disk-sd-donotdelete-clitest-disk-sd-donotdelete-b7e6f082-b310-11eb-8f55-9cfce85d4fa1",
            'policyId2': '/subscriptions/38304e13-357e-405e-9e9a-220351dcce8c/resourceGroups/clitest-dpp-rg/providers/Microsoft.DataProtection/backupVaults/clitest-bkp-vault-persistent-bi-donotdelete/backupPolicies/diskpolicy',
            'policyRuleName': "BackupHourly",
            'permissionsScope': "Resource",
        })
        # Setup
        backup_instance_json = test.cmd('az dataprotection backup-instance initialize --datasource-type "{dataSourceType}" '
                                        '-l "{location}" --policy-id "{policyId2}" --datasource-id "{diskId}" --snapshot-rg "{rg}" '
                                        '--tags Owner=dppclitest Purpose=Testing').get_output_in_json()
        backup_instance_json["backup_instance_name"] = test.kwargs['backupInstanceName2']
        test.kwargs.update({
            "backupInstance2": backup_instance_json,
        })

        # Validations:
        # BI is not listed in vault 2
        # BI is listed in vault 1, with protection enabled
        reset_softdelete_base_state(test)

        # Checks
        # On deleting the BI from a soft-delete-enabled vault, we should still see it under soft deleted items
        test.cmd('az dataprotection backup-instance delete -g "{rg}" --vault-name "{softDeleteVault}" --backup-instance-name "{backupInstanceName1}" --yes')

        test.cmd('az dataprotection backup-instance deleted-backup-instance list -g "{rg}" --vault-name "{softDeleteVault}"', checks=[
            test.greater_than('length([])', 0),
            test.exists("[?name == '{backupInstanceName1}']")
        ])

        test.cmd('az dataprotection backup-instance deleted-backup-instance show -g "{rg}" --vault-name "{softDeleteVault}" --name "{backupInstanceName1}"', checks=[
            test.check('properties.protectionStatus.status', "SoftDeleted")
        ])

        # A soft deleted BI should be available to back up in other vaults
        # Uncomment if validate-for-backup fails due to permission error. Only uncomment if running live.
        # test.cmd('az dataprotection backup-instance update-msi-permissions --datasource-type "{dataSourceType}" --operation Backup --permissions-scope "{permissionsScope}" '
        #          '-g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance2}" --yes')
        # import time
        # time.sleep(60)

        test.cmd('az dataprotection backup-instance validate-for-backup --backup-instance "{backupInstance2}" -g "{rg}" --vault-name "{vaultName}"', checks=[
            test.check('objectType', 'OperationJobExtendedInfo')
        ])

        test.cmd('az dataprotection backup-instance create -g "{rg}" --vault-name "{vaultName}" --backup-instance "{backupInstance2}"', checks=[
            test.check('properties.provisioningState', "Succeeded"),
            test.check('name', "{backupInstanceName2}")
        ])

        # A soft deleted BI can be undeleted anytime, but protection cannot be resumed if it's protected anywhere else
        test.cmd('az dataprotection backup-instance deleted-backup-instance undelete -g "{rg}" --vault-name "{softDeleteVault}" --name "{backupInstanceName1}"')

        test.cmd('az dataprotection backup-instance show -g "{rg}" --vault-name "{softDeleteVault}" --name "{backupInstanceName1}"', checks=[
            test.check('properties.protectionStatus.status', "ProtectionStopped")
        ])

        test.cmd('az dataprotection backup-instance resume-protection -g "{rg}" --vault-name "{softDeleteVault}" --name "{backupInstanceName1}"', expect_failure=True)

        # Once protection elsewhere is stopped, we can resume protection on the undeleted BI
        reset_softdelete_base_state(test)
