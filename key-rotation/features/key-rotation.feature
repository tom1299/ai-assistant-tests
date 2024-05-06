Feature: Sops age key rotation

  Background:
    Given I have the file and folder structure "../../flux"
    And I have the sops configuration file ".sops.yaml"

  Scenario Outline: Get list of files that need to be encrypted
    When I call the python script "../../key_rotation.py" with the following arguments
    | arg_name | arg_value |
    | --age-key | <public_key> |
    | --list-files | |
    | --folder | "../../flux" |
    | --sops-config | "../../flux/.sops.yaml" |
    Then The output should contain this <list> of files
    And the output should not contain this <not_list> of files

    Examples:
      | public_key | list | not_list |
      | age1vzzjtxm5vx6zt5zgxa5g0kvj0h84l88n2rwzkyha49elwdkudczse8mu66 | test/secrets/database/password.yaml, test/tls-secrets/cert.pem, test/tls-secrets/key.pem | test/tls-secrets/tls-secrets.txt |
      | age19c7svc69r96apdtph2x3axmkqn7lypwmqsprnpjf06zjjq2r4epszxlnls | test/tls-secrets/cert.pem, test/tls-secrets/key.pem | test/secrets/database/password.yaml |
      | age1gwwfs5m35aqnrdxwuk3nj7h6539ewlq3kkvu6jlc6drmevueeqdq0mwcg4 | | |

Scenario Outline: Add a new age public key for all entries that contain a given old age public key
  When I call the python script "../../key_rotation.py" with the following arguments
  | arg_name | arg_value |
  | --old-age-key | <old_public_key> |
  | --new-age-key | <new_public_key> |
  | --add-new-key | |
  | --sops-config | "../../flux/.sops.yaml" |
  Then the entries in the sops configuration file containing the old public key <old_public_key> should also contain the new public key <new_public_key>

  Examples:
    | old_public_key | new_public_key |
    | age1vzzjtxm5vx6zt5zgxa5g0kvj0h84l88n2rwzkyha49elwdkudczse8mu66 | age1m4rqtcc8w2c80l485tnnlvhmg05ynaad2y2hx5e3n4wu9gxxxqgsyuecwv |
    | age19c7svc69r96apdtph2x3axmkqn7lypwmqsprnpjf06zjjq2r4epszxlnls | age1afuvjwph326mx2nsjldmj9l0lwr9hz9at62ye82rre5fykvy455s6pdvl3 |