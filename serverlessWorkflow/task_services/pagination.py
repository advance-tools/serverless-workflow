from rest_framework.pagination import CursorPagination


class KeysetPagination(CursorPagination):
    page_size = 100
    page_size_query_param = 'limit'
