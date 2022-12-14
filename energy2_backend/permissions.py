from rest_framework import permissions

class UpdateAndReadOnlyOwned(permissions.BasePermission):
    """
        Permission class allows only Users that are associated with object to update or read it
    """

    def has_permission(self, request, view):
        # any logged in user that wants to retrieve or update a single object gets passed through
        # to has_object_permissions
        if view.action in ['retrieve', 'partial_update', 'update'] and request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        # users can only edit their own
        if request.user == obj.user:
            return True
