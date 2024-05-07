Feature: Sops age key rotation

  Background:
    Given I create a copy of the folder "../../flux" named "flux"
    And I have the script "../../key_rotation.py" as "key_rotation.py"
    And I have the file "../../flux/.sops.yaml" as ".sops.yaml"

  Scenario Outline: Get list of files that need to be encrypted
    When I call the script "key_rotation.py" with the following arguments using the folder "flux" as the current directory
    | arg_name | arg_value |
    | --age-key | <public_key> |
    | --list-files | |
    | --folder | flux |
    | --sops-config | .sops.yaml |
    Then the output should contain this <list> of files from the folder "flux"
    And the output should not contain this <no_list> of files from the folder "flux"

    Examples:
      | public_key | list | not_list |
      | age1vzzjtxm5vx6zt5zgxa5g0kvj0h84l88n2rwzkyha49elwdkudczse8mu66 | test/secrets/database/password.yaml, test/tls-secrets/cert.pem, test/tls-secrets/key.pem | test/tls-secrets/tls-secrets.txt |
      | age19c7svc69r96apdtph2x3axmkqn7lypwmqsprnpjf06zjjq2r4epszxlnls | test/tls-secrets/cert.pem, test/tls-secrets/key.pem | test/secrets/database/password.yaml |
      | age1gwwfs5m35aqnrdxwuk3nj7h6539ewlq3kkvu6jlc6drmevueeqdq0mwcg4 | | |

  Scenario Outline: Add a new age public key for all entries that contain a given old age public key
    When I call the script "key_rotation.py" with the following arguments using the folder "flux" as the current directory
    | arg_name | arg_value |
    | --old-age-key | <old_public_key> |
    | --new-age-key | <new_public_key> |
    | --add-new-key | |
    | --sops-config | ".sops.yaml" |
    Then the entries in the file ".sops.yaml" should contain the old public key <old_public_key> and the new public key <new_public_key>

    Examples:
      | old_public_key | new_public_key |
      | age1vzzjtxm5vx6zt5zgxa5g0kvj0h84l88n2rwzkyha49elwdkudczse8mu66 | age1m4rqtcc8w2c80l485tnnlvhmg05ynaad2y2hx5e3n4wu9gxxxqgsyuecwv |
      | age19c7svc69r96apdtph2x3axmkqn7lypwmqsprnpjf06zjjq2r4epszxlnls | age1afuvjwph326mx2nsjldmj9l0lwr9hz9at62ye82rre5fykvy455s6pdvl3 |