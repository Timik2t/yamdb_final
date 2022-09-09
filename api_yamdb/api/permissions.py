from rest_framework import permissions


class BaseObjPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsReadOnly(BaseObjPermission):
    message = 'Данные доступны только для чтения!'

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdmin(BaseObjPermission):
    message = 'Работа с данными разрешена только администратору!'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(BaseObjPermission):
    message = 'Работа с данными разрешена только модератору!'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator


class IsOwner(permissions.BasePermission):
    message = 'Работа с данными разрешена только автору !'

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
