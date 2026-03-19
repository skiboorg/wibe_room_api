from django.contrib import admin
from .models import Tag, Post, PostPhoto, PostComment, PostReaction, CommentReaction


class PostPhotoInline(admin.TabularInline):
    model = PostPhoto
    extra = 0


class PostReactionInline(admin.TabularInline):
    model = PostReaction
    extra = 0


class CommentReactionInline(admin.TabularInline):
    model = CommentReaction
    extra = 0


class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    readonly_fields = ("date",)
    fk_name = "post"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "community", "date", "added_by")
    inlines = [PostPhotoInline, PostCommentInline, PostReactionInline]


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "parent", "date")
    list_filter = ("post",)
    inlines = [CommentReactionInline]


admin.site.register(Tag)