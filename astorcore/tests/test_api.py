import unittest
import json

from django.test import TestCase
from django.urls import reverse

from taggit.models import Tag


class TagsTest(TestCase):

    def create_tags(self, tags):
        return [ Tag.objects.create(name=tag) for tag in tags ]

    def test_get_request_returns_list_of_tags(self):
        tags = self.create_tags(["my", "first", "tag"])
        response = self.client.get(reverse("api:tag_list"))
        data = json.loads(response.content.decode())
        self.assertEqual(len(data), 3)
        self.assertCountEqual(
            [ tag["name"] for tag in data ], 
            [ tag.name for tag in tags ]
        )

    def test_for_creating_new_tag_with_post_request(self):
        response = self.client.post(reverse("api:tag_list"),
                                    {"name": "Python", "slug": "python"})
        self.assertEqual(response.status_code, 201)
        tag = Tag.objects.first()
        self.assertEqual(tag.name, "Python")

    def test_get_a_tag_by_using_its_slug(self):
        tags = self.create_tags(["tags", "are", "awesome"])
        response = self.client.get(
            reverse("api:tag_detail", kwargs={"slug": tags[0].slug })
        )
        data = json.loads(response.content.decode())
        self.assertEqual(data["id"], tags[0].id)
        self.assertEqual(data["name"], tags[0].name)

    def test_delete_a_with_delete_request(self):
        tags = self.create_tags(["tags", "are", "awesome"])
        response = self.client.delete(
            reverse("api:tag_detail", kwargs={"slug": tags[0].slug })
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Tag.objects.count(), 2)


# Read next part of rest tutorial
# Upgrade your api for tags
# Add tags to show on the list