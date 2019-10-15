# draft code
from AuthSessionExample import AuthentiseSession


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


if __name__ == "__main__":
    print("Running Make Order Example at the command line")

    # build our command line parser
    parser = argparse.ArgumentParser(
        description="Example of getting an API Key for Authentise."
    )
    parser.add_argument("username", help="username to log-in via")
    parser.add_argument("password", help="password to log-in via")
    parser.add_argument("zip_filename", help="Zip file to convert to an order")

    args = parser.parse_args()

    sesh = None
    if "username" in args and "password" in args:
        sesh = AuthentiseSession(host="authentise.com", verify_ssl=True)
        sesh.init_api(args.username, args.password)

    if not sesh:
        LOGGER.error("failed to make a session ")
        exit(1)

    # unpack the data from the zip
    models, metadata = [], {}  # empty entries
    if "zip_filename" in args:
        models, metadata = unpack_zip(args.zip_filename)

    line_item_uris = []
    # for each model, load it, push it to the
    if models and metadata:
        for model in models:
            model_dict = api_dict_from_zip_dict()
            model_uri = sesh.post_and_upload("/model/", model, model_dict)
            line_item_dict = line_item_dict_from_zip_dict(zip_dict)
            line_item_dict["model"] = model_uri
            line_item_uri = sesh.put("/line-tem/", line_item_dict)
            line_item_uris.append(line_item_uri)
    order_dict = order_dict_from_zip(zip_dict)
    order_dict["line-items"] = line_item_uri
    order_uri = sesh.put("/order/", order_dict)
