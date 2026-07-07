from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Common pagination for the project.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):

        return Response({
            "message": data.get("message"),
            "error": data.get("error"),
            "status": 200,
            "pagination": {
                "count": self.page.paginator.count,
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "data": data.get("data"),
        })