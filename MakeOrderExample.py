# draft code
from AuthSessionExample import AuthentiseSession


def upack_zip(filename):
    # code to unpack zip files. Returns metadata-dict, and list of tmp-files of models
    metadata = {"order_anme": "fake order", "files ": []}
    for i in range(0, 3):
        fake_file_dict = {"material": f"Material{i}", "filename": f"filename{i}"}
        metadata["files"].append(fake_file_dict)


def api_dict_from_zip_dict(zip_dict):
    return {}


if __name__ == "__main__":
    print("Running Make Order Example at the command line")

    parser = argparse.ArgumentParser(
        description="Example of getting an API Key for Authentise."
    )
    parser.add_argument("username", help="username to log-in via")
    parser.add_argument("password", help="password to log-in via")
    parser.add_argument("zip_filename", help="Zip file to convert to an order")

    args = parser.parse_args()

    sesh = None
    if "username" in args and "password" in args:
        # print(args)
        sesh = AuthentiseSession(host="authentise.com", verify_ssl=True)
        sesh.init_api(args.username, args.password)

    models, metadata = [], {}  # empty entries
    if ("zip_filename" in args) and sesh:
        models, metadata = unpack_zip(args.zip_filename)

    if models and metadata:
        for model in models:
            model_dict = api_dict_from_zip_dict()
            sesh.post_and_upload("/model/", model, model_dict)
