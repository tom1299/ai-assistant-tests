Feature: Sops age key rotation

  Scenario Outline: Get list of files that need to be encrypted
    Given I have the sops configuration file ".sops.yaml"
    And I the file and folder structure "flux"
    When I call the python script "key_rotation.py" with the command "list-files" and the public age key <public_key>
    Then The output should contain this <list> of files
    And the output should not contain this <not_list> of files

    Examples:
      | public_key | list | not_list |
      | age1vzzjtxm5vx6zt5zgxa5g0kvj0h84l88n2rwzkyha49elwdkudczse8mu66 | test/secrets/database/password.yaml, test/tls-secrets/cert.pem, test/tls-secrets.key.pem | test/tls-secrets/tls-secrets.txt |
      | age19c7svc69r96apdtph2x3axmkqn7lypwmqsprnpjf06zjjq2r4epszxlnls | | |