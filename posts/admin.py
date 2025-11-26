from django.contrib import admin
from .models import Tag, Post, PostPhoto, PostComment, PostReaction

class PostPhotoInline(admin.TabularInline):
    model = PostPhoto
    extra = 0

class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    readonly_fields = ("date",)

class PostReactionInline(admin.TabularInline):
    model = PostReaction
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "community", "date", "added_by")
    inlines = [PostPhotoInline, PostCommentInline, PostReactionInline]

admin.site.register(Tag)
