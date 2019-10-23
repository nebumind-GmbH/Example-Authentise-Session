import argparse

import requests
import json

from requests.auth import HTTPBasicAuth

# pip3 install argparse


class AuthentiseSession:
    # '''
    # Example class to create an API sesssion to a nautilus server for admin use
    # '''

    def __init__(self, host, verify_ssl=True):
        """
        Create an Authentise Session using a persistant API key 
        :param verify_ssl : True/False veirfy SSL Keys to CA's
        :param: host: the site to connect to. For example 'authentise.com' or stage-auth.com' for most customer testing
        """
        self.host = host
        self.session_cookie = None  #
        self.api_auth = None
        self.verify_ssl = verify_ssl

    @staticmethod
    def _parse_session_cookie(cookie):
        parts = cookie.split(";")
        return parts[0]

    def _init_session(self, username, password):
        """
        Creates a connection to the system via username/password to get a cookie
        """
        data = {"username": username, "password": password}

        headers = {"content-type": "application/json"}

        response = requests.post(
            "https://data.{}/sessions/".format(self.host), json=data, headers=headers
        )
        response.raise_for_status()

        cookie_header = response.headers.get("Set-Cookie", None)
        self.session_cookie = self._parse_session_cookie(cookie_header)

    def _get_api_key(self):
        """
        Exaple of fetching the long-term API Key from our api_tokens service.
        Cookie is used to get an API Key (longer term access key) 
        """
        data = {"name": "create-bureau"}

        headers = {"content-type": "application/json", "cookie": self.session_cookie}

        response = requests.post(
            "https://users.{}/api_tokens/".format(self.host),
            json=data,
            headers=headers,
            verify=self.verify_ssl,
        )

        if response.ok:
            self.api_auth = response.json()
            print(" We have received an API key we can re-use")
        else:
            print(" No API key matched.")
            exit(1)  # hard fail

    def init_api(self, username, password):
        """
        Creates a connection to the system. 
        Username / Password to get a Cookie (temporary, expiring key)
        Cookie is used to get an API Key (longer term access key) 
        """
        self._init_session(username, password)
        self._get_api_key()

    def list(self, url, filters=None):
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        list_response = requests.get(
            url.format(self.host), auth=auth, data=filters, verify=self.verify_ssl
        )
        if not list_response.ok:
            return {}
        return list_response.json()

    def post(self, url, data, format_=None):
        "Example of calling the API using the API Key to request data from an endpoint"
        headers = None
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        if format_ == "json":
            headers = {"Content-Type": "application/json"}
            return requests.post(
                url.format(self.host),
                auth=auth,
                json=data,
                verify=self.verify_ssl,
                headers=headers,
            )

        return requests.post(
            url.format(self.host),
            auth=auth,
            data=data,
            verify=self.verify_ssl,
            headers=headers,
        )

    def get_by_url(self, resource_uri):
        """Takes a raw URL, gets the dict of the resource at that location. None on error""" 
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        ret = requests.get( resource_uri, auth=auth, verify=self.verify_ssl)
        if ret.status_code != 200:
            print(f"error getting data on {resource_uri}, got response {ret.text}")
            import pdb; pdb.set_trace()
            return None
        return ret.json()

    def update(self, resource_uri, update_dict): 
        return self.put_(resource_uri, update_dict)

    def put_(self, resource_uri, update_dict): 
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        ret = requests.put( resource_uri, auth=auth, json=update_dict, verify=self.verify_ssl)
        if not ret.ok: 
            print(f"failed to update resource {resource_uri} due to error {ret.text}")
            return False
        return True


    def post_and_upload(self, url, data, file_obj):
        """ does a post to create a resource at 'URL'. 
        If an X-Upload-Location is replied in the heade, the data from file_obj is pushed to that location
        as per the Authentise standard
        """
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        ret = requests.post(
            url.format(self.host), auth=auth, data=data, verify=self.verify_ssl
        )
        if ret.status_code != 201:
            print(f"error posting and upload to {url.format}, got response {ret.text}")
            return None

        # we made the DB resource, upload our data
        resource_url = ret.headers.get("Location")
        upload_url = ret.headers.get("X-Upload-Location")
        if not upload_url:
            print(
                f"Error posting backing-data to to {url.format}, no upload URL in {ret.headers}"
            )
            return None

        # load STL data  from out file , and send to the data service
        raw_data = file_obj.read()  # can take a lot of disk-spcae.
        backing_ret = requests.put(
            upload_url,
            auth=auth,
            data=data,
            headers={"Content-Type": "application/octet-stream"},
        )
        if backing_ret.status_code != 204:
            print(
                f"error uploading backing data for {url.format}, got response {ret.text}"
            )
            return None

        # backing data uploaded . Party
        return resource_url

    def make_delete_request(self, url, uuid):
        "Example of calling the API using the API Key to delete data from an endpoint"
        auth = HTTPBasicAuth(self.api_auth["uuid"], self.api_auth["secret"])
        return requests.delete(url.format(self.host, uuid), auth=auth)

    def get_bureau_uri(self):
        bureau_listicle = self.list("https://data.{}/bureau/")
        # Odd. No match
        if not bureau_listicle.get("resources"):
            print("error, no listing of bureau")
            exit(0)

        # we should have only one match in current releases
        bureau_entry = bureau_listicle.get("resources")[0]
        if not bureau_entry:
            print("error, no details in bureau")
            exit(0)
        return bureau_entry.get("uri")

    def get_any_material_uri(self):
        material_listicle = self.list("https://data.{}/material/")
        if not material_listicle.get("resources"):
            print("error, no listing of material")
            exit(0)
        # we should have only one match in current releases
        material_entry = material_listicle.get("resources")[0]
        if not material_entry:
            print("error, no material in bureau")
            exit(0)
        # returns just our first material we find
        return material_entry.get("uri")

    def get_any_shipping_uri(self):
        listicle = self.list("https://data.{}/shipping/")
        if not listicle.get("resources"):
            print("error, no listing of shipping")
            exit(0)
        # we should have only one match in current releases
        entry = listicle.get("resources")[0]
        if not entry:
            print("error, no shipping in bureau")
            exit(0)
        # returns just our first material we find
        return entry.get("uri")

    def make_request(self, url, data):
        return self.post(url, data)


if __name__ == "__main__":
    print("Running Example AuthSessionExample at the command line")

    parser = argparse.ArgumentParser(
        description="Example of getting an API Key for Authentise."
    )
    parser.add_argument("username", help="username to log-in via")
    parser.add_argument("password", help="password to log-in via")

    args = parser.parse_args()
    if "username" in args and "password" in args:
        # print(args)
        sesh = AuthentiseSession(host="authentise.com", verify_ssl=True)
        sesh.init_api(args.username, args.password)
    # ags should print there error, no else case needed
