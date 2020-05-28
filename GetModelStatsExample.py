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

    model_dict = sesh.get_by_url(new_model_uri)

    print(f"X in mm {model_dict['size']['x']}")
    print(f"Y in mm {model_dict['size']['y']}")
    print(f"Z in mm {model_dict['size']['z']}")
    print(f"Surface Area in MM squared {model_dict['surface_area_mm']}")
    print(f"Volume in MM cubed {model_dict['volume_mm']}")
    print(f"Snapshot link: {model_dict['snapshot_content']}")