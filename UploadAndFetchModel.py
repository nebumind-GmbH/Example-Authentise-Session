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

    print("This script runs for 60 seconds. If the model size is too large to be processed within that time the script will timeout.")
    print("Processing snapshot....")

    # allow time for model to process, otherwise snapshot_content may be None
    time_limit = 60
    timeout = time.time() + time_limit
    got_model_stats = False

    while True:
        if time.time() >= timeout:
            print("Hit script timeout limit. Exiting")
            break

        time.sleep(3)
        model_dict = sesh.get_by_url(new_model_uri)

        if not got_model_stats:
            # if x dimension has been processed, others should be also be processed by now
            if model_dict['size']['x'] is not None:
                print(f"X in mm {model_dict['size']['x']}")
                print(f"Y in mm {model_dict['size']['y']}")
                print(f"Z in mm {model_dict['size']['z']}")
                print(f"Surface Area in MM squared {model_dict['surface_area_mm']}")
                print(f"Volume in MM cubed {model_dict['volume_mm']}")
                got_model_stats = True

        if model_dict['snapshot_content']:
            print(f"Snapshot link: {model_dict['snapshot_content']}")
            break

    if not got_model_stats:
        print(f"Model dimensions and volume/surface area data could not be processed within {str(time_limit)} seconds")

    if model_dict['snapshot_content'] is None:
        print(f"Model snapshot could not be processed within {str(time_limit)} seconds")