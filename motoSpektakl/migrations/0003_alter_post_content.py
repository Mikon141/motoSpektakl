import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('motoSpektakl', '0002_forumthread_post_category_post_dislikes_post_likes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=ckeditor.fields.RichTextField(),
        ),
    ]
