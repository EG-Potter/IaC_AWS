set -eu

#### CONFIGURATION SECTION ####
user_name="ep"
deployment_bucket="${user_name}-deployment-bucket"
aws_profile="generation-de"
#### CONFIGURATION SECTION ####

echo "(*) Creating ${user_name}-deployment-bucket-stack (*)"

aws cloudformation deploy --stack-name ${user_name}-deployment-bucket-stack \
    --template-file deployment-bucket-stack.yml --region eu-west-1 \
    --capabilities CAPABILITY_IAM --profile ${aws_profile};

echo "(*) Install dependencies from requirements-transform.txt into ./transform directory with python 3.9 (*)"

python3 -m pip install --platform manylinux2014_x86_64 \
    --target=./code_templates/transform --implementation cp --python-version 3.9 \
    --only-binary=:all: --upgrade -r requirements-transform.txt --no-user;

echo "(*) Install dependencies from requirements-load.txt into ./load directory with python 3.9 (*)"

python3 -m pip install --platform manylinux2014_x86_64 \
    --target=./code_templates/load --implementation cp --python-version 3.9 \
    --only-binary=:all: --upgrade -r requirements-load.txt --no-user;

echo "(*) Package template and upload local resources to S3 (*)"
echo "(*) A unique S3 filename is automatically generated each time (*)"

aws cloudformation package --template-file etl-stack.yml \
    --s3-bucket ${deployment_bucket} \
    --output-template-file etl-stack-packaged.yml --profile ${aws_profile};

echo "(*) Deploy template (*)"

aws cloudformation deploy --stack-name ${user_name}-etl-process \
    --template-file etl-stack-packaged.yml --region eu-west-1 \
    --capabilities CAPABILITY_IAM --profile ${aws_profile};

echo "(*) Uploading data ... (*)"

# Can remove if sensitive-data-bucket is not needed.
aws s3 cp ./sensitive_data s3://${user_name}-sensitive-data-bucket --recursive --profile ${aws_profile};
# Can remove when fully connected to a data stream.
aws s3 cp ./data_templates s3://${user_name}-data-bucket --recursive --profile ${aws_profile};

echo "...all done!"

echo "statusCode: 200"
