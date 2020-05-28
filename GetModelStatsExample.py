import time
import argparse

from AuthSessionExample import AuthentiseSession
from MakeOrderExample import quick_order_shipping_dict


if __name__ == "__main__":
    print("Running Get Model Stats Example at the command line")

    parser = argparse.ArgumentParser(
            description="Example of getting model stats via API for Authentise."
    )
    parser.add_argument("username", help="username to log-in via")
    parser.add_argument("password", help="password to log-in via")
    parser.add_argument("stl_file", help="path to STL file you would like to upload")
    parser.add_argument(
        "environment", help="The base URL to use with requsts, eg. dev-auth.com for dev or authentise.com for production."
    )

    args = parser.parse_args()

    sesh = None
    if "username" in args and "password" in args:
        sesh = AuthentiseSession(host=args.environment, verify_ssl=True)
        sesh.init_api(args.username, args.password)

    if not sesh:
        LOGGER.error("failed to make a session ")
        exit(1)

    new_model_uri = None
    # upload our model (entry in the db , and file)
    if args.stl_file:
        model_metadata = {"name": str(args.stl_file), "type": "stl"}
        with open(str(args.stl_file), "rb") as file_obj:  # red binary
            new_model_uri = sesh.post_and_upload(
                "https://data.{}/model/", model_metadata, file_obj
            )
            print(f"posted a model. got {new_model_uri}")

    model_dict = sesh.get_by_url(new_model_uri)

    print(f"X in mm {model_dict['size']['x']}")
    print(f"Y in mm {model_dict['size']['y']}")
    print(f"Z in mm {model_dict['size']['z']}")
    print(f"Surface Area in MM squared {model_dict['surface_area_mm']}")
    print(f"Volume in MM cubed {model_dict['volume_mm']}")
    print("Processing snapshot....")

    # allow time for model to process, otherwise snapshot_content may be None
    timeout = time.time() + 15
    while True:
        if time.time() >= timeout:
            print("error processing model")
            break

        time.sleep(1)
        model_dict = sesh.get_by_url(new_model_uri)
        if model_dict['snapshot_content']:
            print(f"Snapshot link: {model_dict['snapshot_content']}")
            break