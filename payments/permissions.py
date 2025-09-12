from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может изменять объект только если он его владелец.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.donator == request.user
