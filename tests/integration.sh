# set -ex: 
# -e stands for 'error' stop the script if there are errors
# -x prints the contents of the script as it runs it
set -ex
curl -sfS http://127.0.0.1:8080 > /dev/null
curl -sfS http://127.0.0.1:8080/login > /dev/null # sfS: silent fail print out failed msg
curl -sfS http://127.0.0.1:8080/logout > /dev/null
# HAVE A GOOD SET OF INTEGRATION TESTS TO ENSURE THERE ARE NO INJECTION ATTACKS POSSIBLE