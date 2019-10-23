# draft code
import argparse
from AuthSessionExample import AuthentiseSession

# Example Usage: python3 UpdateOrderExample.py user@email.com 'User Password!'  "https://data.authentise.com/order/121212"
#
# This is an example of updating an order that exists in Authentise 
#



def quick_order_shipping_dict(shipping_uri):
    s = {
        "address": "dummy address",
        "name": "dummy name",
        "tracking": None,
        "uri": shipping_uri,
    }
    return s


if __name__ == "__main__":
    print("Running Update Order Example at the command line")

    # build our command line parser
    parser = argparse.ArgumentParser(
        description="Example of Updating an order via API for Authentise."
    )
    parser.add_argument("username", help="username to log-in via")
    parser.add_argument("password", help="password to log-in via")
    parser.add_argument("order_uri", help="uri of Order we want to update")

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
    order_dict = None
    if args.order_uri:
       order_dict =  sesh.get_by_url(args.order_uri)

    update_ok = False
    if order_dict: 
        print(f"got details for order {args.order_uri}")
        #update name, as an example: 
        order_update = {'name':'Update + ' + order_dict['name'] }
        update_ok = sesh.update(args.order_uri, order_update) 

    if update_ok: 
        print(f"Updated {args.order_uri} without a poblem")
        exit(0)

    print(f"Updated failed for {args.order_uri} ")
    exit(1)