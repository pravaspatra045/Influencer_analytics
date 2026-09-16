from rest_framework.test import APIClient


class BaseAPITest:

    def setup_method(self):

        self.client = APIClient()
