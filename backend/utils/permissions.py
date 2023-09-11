from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Разрешает доступ только пользователям с ролью администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение на запись доступно только для администраторов,
    для чтения - для всех.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение на запись доступно только для авторов,
    для чтения - для всех.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )


class IsAdminAuthorModeratorOrReadOnly(BasePermission):
    """
    Проверка, является ли пользователь администратором,
    автором или модератором или только чтение.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (not request.user.is_authenticated)
            or (
                request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
            )
        )
