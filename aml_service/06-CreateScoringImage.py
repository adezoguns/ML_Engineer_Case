import os, json, sys
from azureml.core import Workspace
from azureml.core.image import ContainerImage, Image
from azureml.core.model import Model
from azureml.core.authentication import AzureCliAuthentication
cli_auth = AzureCliAuthentication()

# Get workspace
ws = Workspace.from_config(auth=cli_auth)

# Get the latest model details

try:
    with open("aml_config/model.json") as f:
        config = json.load(f)
except:
    print("No new model to register thus no need to create new scoring image")
    sys.exit(0)


model_name_1 = config["attritional_model_name"]
model_version_1 = config["attritional_model_version"]
model_name_2 = config["ll_prop_model_name"]
model_version_2 = config["ll_prop_model_version"]
model_name_3 = config["ll_sev_model_name"]
model_version_3 = config["ll_sev_model_version"]


model_list = Model.list(workspace=ws)
print(model_list)


model_1, = (m for m in model_list if m.version == model_version_1 and m.name == model_name_1)
print(
    "Model picked: {} \nModel Description: {} \nModel Version: {}".format(
        model_1.name, model_1.description, model_1.version
    )
)

model_2, = (m for m in model_list if m.version == model_version_2 and m.name == model_name_2)
print(
    "Model picked: {} \nModel Description: {} \nModel Version: {}".format(
        model_2.name, model_2.description, model_2.version
    )
)

model_3, = (m for m in model_list if m.version == model_version_3 and m.name == model_name_3)
print(
    "Model picked: {} \nModel Description: {} \nModel Version: {}".format(
        model_3.name, model_3.description, model_3.version
    )
)


os.chdir("./code/scoring")
image_name = "fnol-model-score"

image_config = ContainerImage.image_configuration(
    execution_script="score.py",
    runtime="python-slim",
    conda_file="conda_dependencies.yml",
    description="Image for fnol model",
    tags={"area": "FNOL", "type": "regression"},
)

image = Image.create(
    name=image_name, models=[model_1, model_2, model_3], image_config=image_config, workspace=ws
)

image.wait_for_creation(show_output=True)
os.chdir("../..")

if image.creation_state != "Succeeded":
    raise Exception("Image creation status: {image.creation_state}")

print(
    "{}(v.{} [{}]) stored at {} with build log {}".format(
        image.name,
        image.version,
        image.creation_state,
        image.image_location,
        image.image_build_log_uri,
    )
)

# Writing the image details to /aml_config/image.json
image_json = {}
image_json["image_name"] = image.name
image_json["image_version"] = image.version
image_json["image_location"] = image.image_location
with open("aml_config/image.json", "w") as outfile:
    json.dump(image_json, outfile)

print(image_json)