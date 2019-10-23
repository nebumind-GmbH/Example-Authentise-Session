# draft code
import argparse
from AuthSessionExample import AuthentiseSession

# Example Usage: python3 MakeOrderExample.py user@email.com 'User Password!' 10x40mmtower.stl
#
# This is an example of uploading a file to Authentise to create an Order to manufacture
# the attached file.
#
# This uploads a model, creates line-item informaiton on that model, and finally, creates
# an order to track the model's requester and shipping information.


def upack_zip(filename):
    # code to unpack zip files. Returns metadata-dict, and list of tmp-files of models
    metadata = {"order_anme": "fake order", "files ": []}
    for i in range(0, 3):
        fake_file_dict = {"material": f"Material{i}", "filename": f"filename{i}"}
        metadata["files"].append(fake_file_dict)


def model_dict_from_zip(zip_dict):
    """ TBD. unpack zip metadata into model-centric details"""
    return {}


def line_item_dict_from_zip(zip_dict):
    """ TBD. unpack zip metadata into line-item centric details"""
    return {}


def order_dict_from_zip(zip_dict):
    """ TBD. unpack zip metadata into order centric details"""
    return


def quick_order_shipping_dict(shipping_uri):
    s = {
        "address": "dummy address",
        "name": "dummy name",
        "tracking": None,
        "uri": shipping_uri,
    }
    return s


if __name__ == "__main__":
    print("Running Make Order Example at the command line")

    # build our command line parser
    parser = argparse.ArgumentParser(
        description="Example of getting an API Key for Authentise."
    )
    parser.add_argument("username", help="username to log-in via")
    parser.add_argument("password", help="password to log-in via")
    parser.add_argument("stl_file", help="STL file to uploda to an order")

    args = parser.parse_args()

    sesh = None
    if "username" in args and "password" in args:
        sesh = AuthentiseSession(host="authentise.com", verify_ssl=True)
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

    # make a line-item if we have the backing data for it
    new_line_item_uri = None
    if new_model_uri:
        # setup data for our line-item
        line_item_metadata = {}
        line_item_metadata["model"] = new_model_uri
        line_item_metadata["bureau"] = sesh.get_bureau_uri()
        line_item_metadata["materials"] = {
            "base": sesh.get_any_material_uri(),
            "support": None,
        }
        line_item_metadata["quantity"] = 1

        new_line_item_response = sesh.post(
            "https://data.{}/line-item/", line_item_metadata, format_="json"
        )
        if not new_line_item_response.ok:
            print(f"error making line-item {new_line_item_response.text}")
            exit(3)
        new_line_item_uri = new_line_item_response.headers["Location"]
        print(f"new line item at {new_line_item_uri}")

    new_order_uri = None
    if new_line_item_uri:
        order_metadata = {}
        order_metadata["line_items"] = [new_line_item_uri]
        order_metadata["bureau"] = sesh.get_bureau_uri()
        order_metadata["name"] = "New Order for " + str(model_metadata["name"])
        order_metadata["currency"] = "USD"
        order_metadata["shipping"] = quick_order_shipping_dict(
            sesh.get_any_shipping_uri()
        )
        new_order_response = sesh.post(
            "https://data.{}/order/", order_metadata, format_="json"
        )
        if not new_order_response.ok:
            print(f"new order creation error {new_order_response.text} ")
            exit(5)  # error
        new_order_uri = new_order_response.headers["Location"]
        print(f"new order at {new_order_uri}")
        exit(0)
    print(f"no new order created.")
