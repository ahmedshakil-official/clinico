# import uuid
# from easy_thumbnails.fields import ThumbnailerImageField
# from django.db import models
#
#
# class TimestampThumbnailImageField(ThumbnailerImageField):
#     def generate_filename(self, instance, filename):
#         """Add timestamp at beginning of the file name"""
#         # Adding a timestamp at the beginning of the file name
#         new_filename = "{}_{}".format(uuid.uuid4().hex, filename)
#         filename = super(TimestampThumbnailImageField, self).generate_filename(
#             instance, new_filename
#         )
#         return filename
