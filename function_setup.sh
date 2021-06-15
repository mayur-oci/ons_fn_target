OCI_TENANCY_NAME=intrandallbarnes
OCI_TENANCY_OCID=ocid1.tenancy.oc1..aaaaaaaaopbu45aomik7sswe4nzzll3f6ii6pipd5ttw4ayoozez37qqmh3a

OCI_HOME_REGION=us-ashburn-1
OCI_CURRENT_REGION=us-sanjose-1 # from OCI config file
OCI_CURRENT_REGION_CODE=sjc
OCI_CLI_PROFILE=DEFAULT

OCI_CMPT_ID=ocid1.compartment.oc1..aaaaaaaa2z4wup7a4enznwxi3mkk55cperdk3fcotagepjnan5utdb3tvakq

FN_CONTEXT=fn_oss_cntx_June2021
FN_APP_NAME=ons_fn_app
FN_NAME=ons_fn_target
fn delete context $FN_CONTEXT # just to make script idempotent
fn create context $FN_CONTEXT --provider oracle
fn use context $FN_CONTEXT
fn update context oracle.compartment-id $OCI_CMPT_ID
fn update context api-url "https://functions.${OCI_CURRENT_REGION}.oraclecloud.com" # this is the OCI fn service url, again this is region specific
fn update context oracle.profile $OCI_CLI_PROFILE
fn update context registry sjc.ocir.io/intrandallbarnes/ons_fn_target

fn list apps
TAIL_URL=tcp://logs5.papertrailapp.com:45170 #optional
if [ ! -z "$TAIL_URL" ]; then
   fn update app $FN_APP_NAME --syslog-url $TAIL_URL
fi
docker login -u 'intrandallbarnes/mayur.raleraskar@oracle.com' -p 'auth_token_from_oci' sjc.ocir.io
fn -v deploy --app $FN_APP_NAME --no-bump

DEBUG=1 fn invoke $FN_APP_NAME $FN_NAME < test_alarm_message.json
